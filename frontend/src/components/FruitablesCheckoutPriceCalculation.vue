<script setup>
import { ref, computed } from 'vue';
import FruitablesCheckoutTableRow from '@/components/FruitablesCheckoutTableRow.vue';

// 定義 props 來接收 products 資料
const props = defineProps({
  products: {
    type: Array,
    required: true,
    default: () => []
  }
});

// 新增運費選擇的響應式變數
const selectedShipping = ref(0);

// 計算商品總額
const subtotal = computed(() => {
  return props.products.reduce((sum, product) => {
    return sum + (product.price * product.quantity)
  }, 0);
});

// 計算最終總額 (商品總額 + 運費)
const total = computed(() => {
  return subtotal.value + selectedShipping.value;
});

// 處理運費選擇
const handleShippingChange = (fee) => {
  selectedShipping.value = fee;
};
</script>

<template>
<!-- 價格計算 component (FruitablesCheckoutPriceCalculation.vue)-->
    <div class="table-responsive 父組件highlight">
        <table class="table">
            <thead>
                <tr>
                    <th scope="col">Products 圖片</th>
                    <th scope="col">Name 品名</th>
                    <th scope="col">Price 單價</th>
                    <th scope="col">Quantity 數量</th>
                    <th scope="col">Total 總計</th>
                </tr>
            </thead>
            <tbody>
                <!-- 品項列 component (FruitablesCheckoutTableRow.vue)-->
                <FruitablesCheckoutTableRow
                    v-for="product in props.products"
                    :key="product.id"
                    :product="product"
                />

                <tr>
                    <th scope="row">
                    </th>
                    <td class="py-5">
                        <p class="mb-0 text-dark py-4">Shipping 運費</p>
                    </td>
                    <td colspan="3" class="py-5">
                        <div class="form-check text-start">
                            <!-- 金額計算主要是從屬性裡的:value=""改而非只有改<label>的文字喔 -->
                            <input type="radio" class="form-check-input bg-primary border-0" 
                                   id="Shipping-1" name="Shipping-1" :value="0"
                                   @change="handleShippingChange(0)">
                            <label class="form-check-label" for="Shipping-1">自取免運費</label>
                        </div>
                        <div class="form-check text-start">
                            <input type="radio" class="form-check-input bg-primary border-0" 
                                   id="Shipping-2" name="Shipping-1" :value="15"
                                   @change="handleShippingChange(15)">
                            <label class="form-check-label" for="Shipping-2">空運 : $15.00</label>
                        </div>
                        <div class="form-check text-start">
                            <input type="radio" class="form-check-input bg-primary border-0" 
                                   id="Shipping-3" name="Shipping-1" :value="8"
                                   @change="handleShippingChange(8)">
                            <label class="form-check-label" for="Shipping-3">海運 : $8.00</label>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th scope="row">
                    </th>
                    <td class="py-5">
                        <p class="mb-0 text-dark text-uppercase py-3">TOTAL 總計</p>
                    </td>
                    <td class="py-5"></td>
                    <td class="py-5"></td>
                    <td class="py-5">
                        <div class="py-3 border-bottom border-top">
                            <p class="mb-0 text-dark">${{ total.toFixed(2) }}</p>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style>
</style>