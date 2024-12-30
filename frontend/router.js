import { createWebHistory, createRouter } from "vue-router";
// 專題用視圖
import HomeView from "./views/HomeView.vue";
import CommissionView from "./views/CommissionView.vue";
import LoginView from "./views/member/LoginView.vue";
import SignupView from "./views/member/SignupView.vue";
import ResetView from "./views/member/ResetView.vue";
import ResetPasswordView from "./views/member/ResetPasswordView.vue";
import ResetVerifyView from "./views/member/ResetVerifyView.vue";
import CenterView from "./views/member/CenterView.vue";
import CenterPlusView from "./views/member/CenterPlusView.vue";
import VerifyEmailView from "./views/member/VerifyEmailView.vue";
import NotFound from "./views/404View.vue";

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
},
{
    //http://localhost:5173/center-plus  => 載入 CenterPlusView 進階設定
    path: '/center-plus/:user_id',
    name: 'center_plus',
    component: CenterPlusView,
    props: true,
},

// 以下為 Pages範例模板 連結
{
    //http://localhost:5173/Fruitables  => 載入 FruitablesHomeView
    path:'/Fruitables', 
    component:FruitablesHomeView,
    name:'Fruitables_Home',
    alias:'/Fruitables/index'
},
{
    //http://localhost:5173/Fruitables/shop  => 載入 FruitablesShopView
    path:'/Fruitables/shop',
    component:FruitablesShopView,
    name:'Fruitables_Shop',
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
    routes
})

// 全局路由守卫
// router.beforeEach((to, from, next) => {
//     const isLoggedIn = !!localStorage.getItem('memberData'); // 檢查是否已登入

//     if (!isLoggedIn && to.name !== 'login') {
//         // 如果沒登入且試圖訪問非登錄頁，就重新導向到登錄頁
//         next({ name: 'login' });
//     } else if (isLoggedIn && to.name === 'login') {
//         // 如果有登入卻試圖訪問登錄頁，就重新導向到會員中心
//         next({ name: 'center' });
//     } else {
//         // 其他情况放行
//         next();
//     }
// });

export default router