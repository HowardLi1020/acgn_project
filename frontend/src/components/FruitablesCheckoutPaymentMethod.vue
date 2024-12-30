<script setup>

</script>

<template>
<!-- 付款方式 component (FruitablesCheckoutPaymentMethod.vue)-->
<div class="父組件highlight">
    <div class="row g-4 text-center align-items-center justify-content-center border-bottom py-3">
        <div class="col-12">
            <div class="form-check text-start my-3">
            <input type="checkbox" class="form-check-input bg-primary border-0" id="Transfer-1" name="Transfer" value="Transfer">
            <label class="form-check-label" for="Transfer-1">Direct Bank Transfer</label>
        </div>
        <p class="text-start text-dark">Make your payment directly into our bank account. Please use your Order ID as the payment reference. Your order will not be shipped until the funds have cleared in our account.</p>
    </div>
    </div>
    <div class="row g-4 text-center align-items-center justify-content-center border-bottom py-3">
        <div class="col-12">
            <div class="form-check text-start my-3">
                <input type="checkbox" class="form-check-input bg-primary border-0" id="Payments-1" name="Payments" value="Payments">
                <label class="form-check-label" for="Payments-1">Check Payments</label>
            </div>
        </div>
    </div>
    <div class="row g-4 text-center align-items-center justify-content-center border-bottom py-3">
        <div class="col-12">
            <div class="form-check text-start my-3">
                <input type="checkbox" class="form-check-input bg-primary border-0" id="Delivery-1" name="Delivery" value="Delivery">
                <label class="form-check-label" for="Delivery-1">Cash On Delivery</label>
            </div>
        </div>
    </div>
    <div class="row g-4 text-center align-items-center justify-content-center border-bottom py-3">
        <div class="col-12">
            <div class="form-check text-start my-3">
                <input type="checkbox" class="form-check-input bg-primary border-0" id="Paypal-1" name="Paypal" value="Paypal">
                <label class="form-check-label" for="Paypal-1">Paypal</label>
            </div>
        </div>
    </div>
</div>
</template>

<style>
</style>