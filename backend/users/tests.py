from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Department, Group, Student, Teacher


User = get_user_model()


class UserModelTests(TestCase):
    def test_user_string_representation_uses_full_name(self):
        user = User.objects.create_user(
            username='student_user',
            email='student_user@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Ivan',
            last_name='Petrov',
            middle_name='Sergeevich',
        )

        self.assertEqual(str(user), 'Petrov Ivan Sergeevich')

    def test_role_properties_match_user_role(self):
        student = User.objects.create_user(
            username='student_role',
            email='student_role@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='Role',
        )
        teacher = User.objects.create_user(
            username='teacher_role',
            email='teacher_role@example.com',
            password='Pass12345!',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='Role',
        )

        self.assertTrue(student.is_student)
        self.assertFalse(student.is_teacher)
        self.assertTrue(teacher.is_teacher)
        self.assertFalse(teacher.is_student)


class StudentTeacherModelTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(number='A-01')
        self.department = Department.objects.create(name='Computer Science')

    def test_student_save_requires_student_role(self):
        teacher_user = User.objects.create_user(
            username='teacher_for_student',
            email='teacher_for_student@example.com',
            password='Pass12345!',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='Wrong',
        )

        with self.assertRaises(ValidationError):
            Student.objects.create(user=teacher_user, group_number=self.group)

    def test_teacher_save_requires_teacher_role(self):
        student_user = User.objects.create_user(
            username='student_for_teacher',
            email='student_for_teacher@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='Wrong',
        )

        with self.assertRaises(ValidationError):
            Teacher.objects.create(user=student_user, department=self.department)

    def test_related_models_string_representation(self):
        student_user = User.objects.create_user(
            username='student_repr',
            email='student_repr@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='Repr',
        )
        teacher_user = User.objects.create_user(
            username='teacher_repr',
            email='teacher_repr@example.com',
            password='Pass12345!',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='Repr',
        )
        student = Student.objects.create(user=student_user, group_number=self.group)
        teacher = Teacher.objects.create(user=teacher_user, department=self.department)

        self.assertEqual(str(self.group), 'A-01')
        self.assertEqual(str(self.department), 'Computer Science')
        self.assertEqual(str(student), str(student_user))
        self.assertEqual(str(teacher), str(teacher_user))


class CreateSuperuserCommandTests(TestCase):
    def test_createsuperuser_command_supports_required_custom_fields(self):
        stdout = StringIO()

        call_command(
            'createsuperuser',
            '--noinput',
            username='cmd_admin',
            email='cmd_admin@example.com',
            role=User.Role.TEACHER,
            stdout=stdout,
        )

        user = User.objects.get(username='cmd_admin')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, User.Role.TEACHER)
        self.assertEqual(user.email, 'cmd_admin@example.com')


class UsersApiTests(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(number='B-02')
        self.department = Department.objects.create(name='Mathematics')
        self.student_user = User.objects.create_user(
            username='student_one',
            email='student_one@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='One',
            middle_name='Middle',
            contacts='student contacts',
        )
        self.other_student = User.objects.create_user(
            username='student_two',
            email='student_two@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='Two',
        )
        self.teacher_user = User.objects.create_user(
            username='teacher_one',
            email='teacher_one@example.com',
            password='Pass12345!',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='One',
        )
        self.student_profile = Student.objects.create(user=self.student_user, group_number=self.group)
        Student.objects.create(user=self.other_student, group_number=self.group)
        Teacher.objects.create(user=self.teacher_user, department=self.department, is_norm_controller=True)

        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.refresh_url = reverse('refresh')
        self.logout_url = reverse('logout')
        self.me_url = reverse('me')

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh

    def test_register_creates_student_profile_and_returns_tokens(self):
        payload = {
            'username': 'new_student',
            'email': 'new_student@example.com',
            'password': 'StrongPass123!',
            'last_name': 'Studentov',
            'first_name': 'New',
            'middle_name': 'Middle',
            'contacts': 'new contacts',
            'group_number': self.group.id,
        }

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(username='new_student')
        self.assertEqual(created_user.role, User.Role.STUDENT)
        self.assertTrue(created_user.check_password('StrongPass123!'))
        self.assertTrue(Student.objects.filter(user=created_user, group_number=self.group).exists())
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['role'], User.Role.STUDENT)
        self.assertNotIn('password', response.data)

    def test_register_requires_group_number(self):
        payload = {
            'username': 'student_no_group',
            'email': 'student_no_group@example.com',
            'password': 'StrongPass123!',
            'last_name': 'Studentov',
            'first_name': 'NoGroup',
        }

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('group_number', response.data)

    def test_register_rejects_weak_password(self):
        payload = {
            'username': 'weak_password_user',
            'email': 'weak_password_user@example.com',
            'password': '12345678',
            'last_name': 'Weak',
            'first_name': 'Password',
            'group_number': self.group.id,
        }

        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_returns_token_pair_for_valid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'username': 'student_one', 'password': 'Pass12345!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_returns_token_pair_for_valid_email_credentials(self):
        response = self.client.post(
            self.login_url,
            {'email': 'student_one@example.com', 'password': 'Pass12345!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'username': 'student_one', 'password': 'wrong-password'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_refresh_returns_new_access_token(self):
        refresh = RefreshToken.for_user(self.student_user)

        response = self.client.post(
            self.refresh_url,
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_refresh_rejects_invalid_token(self):
        response = self.client.post(
            self.refresh_url,
            {'refresh': 'invalid-token'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user_profile(self):
        self.authenticate(self.student_user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.student_user.username)
        self.assertEqual(response.data['email'], self.student_user.email)
        self.assertEqual(response.data['role'], User.Role.STUDENT)
        self.assertFalse(response.data['is_staff'])
        self.assertFalse(response.data['is_superuser'])
        self.assertEqual(response.data['group_id'], self.group.id)
        self.assertEqual(response.data['group_number'], self.group.number)

    def test_me_returns_teacher_specific_profile_fields(self):
        self.authenticate(self.teacher_user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], User.Role.TEACHER)
        self.assertEqual(response.data['department_id'], self.department.id)
        self.assertEqual(response.data['department_name'], self.department.name)
        self.assertTrue(response.data['is_norm_controller'])
        self.assertIsNone(response.data['student_limit'])

    def test_me_patch_updates_current_student_profile(self):
        self.authenticate(self.student_user)

        payload = {
            'email': 'updated_student@example.com',
            'first_name': 'Updated',
            'contacts': 'updated contacts',
        }

        response = self.client.patch(self.me_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.email, payload['email'])
        self.assertEqual(self.student_user.first_name, payload['first_name'])
        self.assertEqual(self.student_user.contacts, payload['contacts'])
        self.assertEqual(response.data['group_id'], self.group.id)
        self.assertEqual(response.data['group_number'], self.group.number)

    def test_me_patch_updates_current_teacher_profile(self):
        self.authenticate(self.teacher_user)

        payload = {
            'last_name': 'UpdatedTeacher',
            'contacts': 'teacher contacts',
        }

        response = self.client.patch(self.me_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher_user.refresh_from_db()
        self.assertEqual(self.teacher_user.last_name, payload['last_name'])
        self.assertEqual(self.teacher_user.contacts, payload['contacts'])
        self.assertEqual(response.data['department_id'], self.department.id)
        self.assertEqual(response.data['department_name'], self.department.name)

    def test_me_patch_rejects_duplicate_email(self):
        self.authenticate(self.student_user)

        response = self.client.patch(
            self.me_url,
            {'email': self.teacher_user.email},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_logout_blacklists_current_users_refresh_token(self):
        refresh = self.authenticate(self.student_user)

        response = self.client.post(self.logout_url, {'refresh': str(refresh)}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'detail': 'Successfully logged out.'})
        self.assertTrue(
            BlacklistedToken.objects.filter(token__jti=refresh['jti']).exists()
        )

    def test_logout_requires_authentication(self):
        refresh = RefreshToken.for_user(self.student_user)

        response = self.client.post(self.logout_url, {'refresh': str(refresh)}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_rejects_another_users_refresh_token(self):
        own_refresh = self.authenticate(self.student_user)
        other_refresh = RefreshToken.for_user(self.other_student)

        response = self.client.post(self.logout_url, {'refresh': str(other_refresh)}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You can only revoke your own refresh token.')
        self.assertFalse(
            BlacklistedToken.objects.filter(token__jti=other_refresh['jti']).exists()
        )
        self.assertFalse(
            BlacklistedToken.objects.filter(token__jti=own_refresh['jti']).exists()
        )

    def test_logout_rejects_invalid_refresh_token(self):
        self.authenticate(self.student_user)

        response = self.client.post(self.logout_url, {'refresh': 'invalid-token'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid or expired refresh token.')
