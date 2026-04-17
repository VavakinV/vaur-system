import {createStore} from "vuex"
import { authModule } from "@/store/modules/authModule"

export default createStore({
    modules: {
        auth: authModule
    }
})