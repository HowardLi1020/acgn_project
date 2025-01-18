import { createWebHistory, createRouter } from "vue-router";
// 專題用視圖
import HomeView from "./views/HomeView.vue";
import CommissionView from "./views/CommissionView.vue";
import NotFound from "./views/404View.vue";

// Member
import LoginView from "./views/member/LoginView.vue";
import SignupView from "./views/member/SignupView.vue";
import VerifyEmailView from "./views/member/VerifyEmailView.vue";
import CenterView from "./views/member/CenterView.vue";
import CenterPlusView from "./views/member/CenterPlusView.vue";
import ResetView from "./views/member/ResetView.vue";
import ResetVerifyView from "./views/member/ResetVerifyView.vue";
import ResetPasswordView from "./views/member/ResetPasswordView.vue";
import PhoneChangeView from "./views/member/PhoneChangeView.vue";
import PhoneVerifyView from "./views/member/PhoneVerifyView.vue";
import PhoneResetView from "./views/member/PhoneResetView.vue";
import EmailChangeView from "./views/member/EmailChangeView.vue";
import EmailVerifyView from "./views/member/EmailVerifyView.vue";
import EmailResetView from "./views/member/EmailResetView.vue";
import VerifyLineView from "./views/member/VerifyLineView.vue";


// Store
import StoreView from "./views/Store/StoreView.vue";
import ProductDetail from "./views/Store/ProductDetail.vue";
import CreateProduct from "./views/Store/CreateProduct.vue";
import MyProduct from "./views/Store/MyProduct.vue";
import EditProduct from "./views/Store/EditProduct.vue";

// Cart
import CartView from '@/views/cart/CartView.vue'; // 確保 @ 指向 src/
import Checkout from "./views/cart/Checkout.vue";

// 導入 Pages範例模板
import FruitablesHomeView from "./views/FruitablesHomeView.vue";
import FruitablesShopView from "./views/FruitablesShopView.vue";
import FruitablesDetailView from "./views/FruitablesDetailView.vue";
import FruitablesContactView from "./views/FruitablesContactView.vue";
import FruitablesCartView from "./views/FruitablesCartView.vue";
import FruitablesCheckoutView from "./views/FruitablesCheckoutView.vue";


//路由設定 path 比對 URL，比對成功就載入對應的組件
const routes =[
{
    //http://localhost:5173/  => 載入 HomeView
    path:'/', 
    component:HomeView,
    name:'Home',
    alias:'/index'
},
{
    //http://localhost:5173/commission  => 載入 CommissionView
    path:'/commission',
    component:CommissionView,
    name:'Commission',
    // redirect:'/commission/overview',
    // children:[
    //   {
    //     //http://localhost:5173/commission/need
    //     path:'need', 
    //     component:CommissionNeedView, 
    //     name:'Need'
    //   },
    //   {
    //     //http://localhost:5173/commission/work
    //     path:'work', 
    //     component:CommissionWorkView, 
    //     name:'Work'
    //   },
    //  {
    //     //http://localhost:5173/commission/public_card
    //     path:'public_card', 
    //     component:CommissionPublicCardView, 
    //     name:'Public_Card'
    //   },
    // ]
},

// Member
{
    //http://localhost:5173/login  => 載入 LoginView 登入
    path: '/login',
    name: 'login',
    component: LoginView,
},
{
    //http://localhost:5173/signup  => 載入 SignupView 註冊
    path: '/signup',
    name: 'signup',
    component: SignupView,
},
{
    //http://localhost:5173/verify-email/:token'  => 載入 VerifyEmail 註冊驗證
    path: '/verify-email/:token',
    name: 'VerifyEmail',
    component: VerifyEmailView,
},
{
    //http://localhost:5173/reset  => 載入 ResetView 發起重置
    path: '/reset',
    name: 'Reset',
    component: ResetView,
},
{
    //http://localhost:5173/reset-verify/:code  => 載入 ResetVerifyView 提示重置驗證
    path: '/reset-verify/:code',
    name: 'ResetVerify',
    component: ResetVerifyView,
},
{
    //http://localhost:5173/reset-password  => 載入 ResetPasswordView  進入重置密碼
    path: '/reset-password',
    name: 'ResetPw',
    component: ResetPasswordView,
},
{
    //http://localhost:5173/center  => 載入 CenterView 會員中心
    path: '/center/:user_id',
    name: 'center',
    component: CenterView,
    props: true,
    meta: { requiresAuth: true }    // 需要驗證
},
{
    //http://localhost:5173/center-plus  => 載入 CenterPlusView 進階設定
    path: '/center-plus/:user_id',
    name: 'center_plus',
    component: CenterPlusView,
    props: true,
    meta: { requiresAuth: true }    // 需要驗證
},
{
    //http://localhost:5173/phone-change  => 載入 PhoneChangeView 發起 修改手機
    path: '/phone-change',
    name: 'PhoneChange',
    component: PhoneChangeView,
},
{
    //http://localhost:5173/phone-verify/:code  => 載入 PhoneVerifyView 提示修改手機驗證
    path: '/phone-verify/:code',
    name: 'PhoneVerify',
    component: PhoneVerifyView,
},
{
    //http://localhost:5173/phone-reset  => 載入 PhoneResetView 進行 修改手機
    path: '/phone-reset',
    name: 'PhoneReset',
    component: PhoneResetView,
},
{
    //http://localhost:5173/email-change  => 載入 EmailChangeView 發起 修改電子郵件
    path: '/email-change',
    name: 'EmailChange',
    component: EmailChangeView,
},
{
    //http://localhost:5173/email-verify/:code  => 載入 EmailVerifyView 提示修改電子郵件驗證
    path: '/email-verify/:code',
    name: 'EmailVerify',
    component: EmailVerifyView,
},
{
    //http://localhost:5173/email-reset  => 載入 EmailResetView 進行 修改電子郵件
    path: '/email-reset',
    name: 'EmailReset',
    component: EmailResetView,
},
{
    //http://localhost:5173/verify-line  => 載入 VerifyLineView 進行 驗證Line
    path: '/verify-line',
    name: 'VerifyLine',
    component: VerifyLineView,
},

// Store
{
    //http://localhost:5173/store
    path:'/store',
    component:StoreView,
    name:'store',
},
{
    path: '/store/product/:id', // 使用動態路由參數
    name: 'ProductDetail',
    component:ProductDetail,
},
{
    path: '/store/create-product', // 添加創建商品的路由
    component: CreateProduct,
    name: 'CreateProduct',
},
{
    path: '/store/my-products', // 添加創建商品的路由
    component: MyProduct,
    name: 'MyProduct',
},
{
    path: '/store/edit-product/:productId', // 添加創建商品的路由
    component: EditProduct,
    name: 'EditProduct',
},

{
    path: '/shoppingcart',
    name: 'ShoppingCart',
    component: CartView,
},

{
    path: '/checkout',
    name: 'Checkout',
    component: Checkout,
},

// 以下為 Pages範例模板 連結
{
    //http://localhost:5173/store  => 載入 FruitablesHomeView
    path:'/Fruitables', 
    component:FruitablesHomeView,
    name:'Fruitables_Home',
    alias:'/Fruitables/index'
},

{
    //http://localhost:5173/Fruitables/detail  => 載入 FruitablesDetailView
    path:'/Fruitables/detail',
    component:FruitablesDetailView,
    name:'Fruitables_Shop_Detail',
},
{
    //http://localhost:5173/Fruitables/contact  => 載入 FruitablesContactView
    path:'/Fruitables/contact',
    component:FruitablesContactView,
    name:'Fruitables_Contact',
},
{
    //http://localhost:5173/cart  => 載入 FruitablesCartView
    path:'/Fruitables/cart',
    component:FruitablesCartView,
    name:'Fruitables_Cart',
},
{
    //http://localhost:5173/Fruitables/checkout  => 載入 FruitablesCheckoutView
    path:'/Fruitables/checkout',
    component:FruitablesCheckoutView,
    name:'Fruitables_Checkout',
},
{
  //404
    path:'/:pathMatch(.*)*',
    component:NotFound
}]

const router = createRouter({
    history:createWebHistory(),  //HTML5 History API
    routes,
})

export default router;