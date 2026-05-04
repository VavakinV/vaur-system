import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import Department, Group, Student, Teacher
from works.models import Work, WorkType


User = get_user_model()


@override_settings(
    USE_S3_STORAGE=False,
    STORAGES={
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)
class WorkDocumentApiTests(APITestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.override.enable()

        self.group = Group.objects.create(number='DOC-01')
        self.department = Department.objects.create(name='Document Department')
        self.work_type = WorkType.objects.create(name='Course work')

        self.student_user = User.objects.create_user(
            username='student_doc',
            email='student_doc@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='Doc',
        )
        self.other_student_user = User.objects.create_user(
            username='student_other',
            email='student_other@example.com',
            password='Pass12345!',
            role=User.Role.STUDENT,
            first_name='Other',
            last_name='Student',
        )
        self.supervisor_user = User.objects.create_user(
            username='teacher_doc',
            email='teacher_doc@example.com',
            password='Pass12345!',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='Doc',
        )
        self.norm_controller_user = User.objects.create_user(
            username='teacher_norm',
            email='teacher_norm@example.com',
            password='Pass12345!',
            role=User.Role.TEACHER,
            first_name='Norm',
            last_name='Controller',
        )

        self.student = Student.objects.create(user=self.student_user, group_number=self.group)
        Student.objects.create(user=self.other_student_user, group_number=self.group)
        self.supervisor = Teacher.objects.create(
            user=self.supervisor_user,
            department=self.department,
            is_norm_controller=False,
        )
        self.norm_controller = Teacher.objects.create(
            user=self.norm_controller_user,
            department=self.department,
            is_norm_controller=True,
        )

        self.work = Work.objects.create(
            student=self.student,
            supervisor=self.supervisor,
            department=self.department,
            work_type=self.work_type,
            topic='Test work topic',
        )
        self.url = reverse('work-document', args=[self.work.pk])

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.temp_media_root, ignore_errors=True)

    def authenticate(self, user):
        response = self.client.post(
            reverse('login'),
            {'username': user.username, 'password': 'Pass12345!'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_student_can_upload_docx_document(self):
        self.authenticate(self.student_user)
        document = SimpleUploadedFile(
            'thesis.docx',
            b'docx content',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

        response = self.client.post(self.url, {'document': document}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.work.refresh_from_db()
        self.assertTrue(self.work.document.name.endswith('.docx'))
        self.assertEqual(self.work.document_original_name, 'thesis.docx')
        self.assertTrue(response.data['has_document'])
        self.assertTrue(response.data['download_url'].endswith(self.url))

    def test_model_save_updates_original_name_for_direct_file_assignment(self):
        self.work.document_original_name = 'stale-name.docx'
        self.work.document = SimpleUploadedFile(
            'admin-upload.docx',
            b'docx content',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

        self.work.save()
        self.work.refresh_from_db()

        self.assertEqual(self.work.document_original_name, 'admin-upload.docx')

    def test_model_save_clears_original_name_when_document_removed(self):
        self.work.document = SimpleUploadedFile(
            'remove-me.docx',
            b'docx content',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        self.work.save()
        self.work.document.delete(save=False)
        self.work.document = None

        self.work.save()
        self.work.refresh_from_db()

        self.assertEqual(self.work.document_original_name, '')

    def test_upload_rejects_non_docx_file(self):
        self.authenticate(self.student_user)
        document = SimpleUploadedFile(
            'notes.pdf',
            b'pdf content',
            content_type='application/pdf',
        )

        response = self.client.post(self.url, {'document': document}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('document', response.data)

    def test_other_student_cannot_upload_document(self):
        self.authenticate(self.other_student_user)
        document = SimpleUploadedFile(
            'thesis.docx',
            b'docx content',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )

        response = self.client.post(self.url, {'document': document}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_supervisor_can_download_document(self):
        self.work.document.save('supervised.docx', SimpleUploadedFile('supervised.docx', b'docx data'), save=True)
        self.work.document_original_name = 'supervised.docx'
        self.work.save(update_fields=['document_original_name'])
        self.authenticate(self.supervisor_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('supervised.docx', response['Content-Disposition'])

    def test_norm_controller_can_download_document(self):
        self.work.document.save('controlled.docx', SimpleUploadedFile('controlled.docx', b'docx data'), save=True)
        self.work.document_original_name = 'controlled.docx'
        self.work.save(update_fields=['document_original_name'])
        self.authenticate(self.norm_controller_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_requires_uploaded_document(self):
        self.authenticate(self.student_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Файл работы не загружен.')

    def test_download_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_can_get_short_work_info(self):
        self.authenticate(self.student_user)

        response = self.client.get(reverse('work-short', args=[self.work.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.work.pk)
        self.assertEqual(response.data['topic'], self.work.topic)
        self.assertEqual(response.data['student_full_name'], str(self.student_user))
        self.assertEqual(response.data['supervisor_full_name'], str(self.supervisor_user))
        self.assertEqual(response.data['department_name'], self.department.name)
        self.assertEqual(response.data['work_type_name'], self.work_type.name)
        self.assertFalse(response.data['has_document'])

    def test_supervisor_can_get_detailed_work_info(self):
        self.work.document.save('detailed.docx', SimpleUploadedFile('detailed.docx', b'docx data'), save=True)
        self.work.document_original_name = 'detailed.docx'
        self.work.save(update_fields=['document_original_name'])
        self.authenticate(self.supervisor_user)

        response = self.client.get(reverse('work-detail', args=[self.work.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.work.pk)
        self.assertEqual(response.data['student_id'], self.student.pk)
        self.assertEqual(response.data['supervisor_id'], self.supervisor.pk)
        self.assertEqual(response.data['department_id'], self.department.pk)
        self.assertEqual(response.data['work_type_id'], self.work_type.pk)
        self.assertEqual(response.data['document_original_name'], 'detailed.docx')
        self.assertTrue(response.data['download_url'].endswith(reverse('work-document', args=[self.work.pk])))

    def test_other_student_cannot_get_short_work_info(self):
        self.authenticate(self.other_student_user)

        response = self.client.get(reverse('work-short', args=[self.work.pk]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_work_detail_requires_authentication(self):
        response = self.client.get(reverse('work-detail', args=[self.work.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
