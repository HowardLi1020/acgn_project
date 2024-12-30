<script setup>

</script>

<template>
<!-- 收件資訊 component (FruitablesCheckoutForm.vue)-->
    <div class="col-md-12 col-lg-6 col-xl-7 父組件highlight">
        <div class="row">
            <div class="col-md-12 col-lg-6">
                <div class="form-item w-100">
                    <label class="form-label my-3">First Name<sup>*</sup></label>
                    <input type="text" class="form-control">
                </div>
            </div>
            <div class="col-md-12 col-lg-6">
                <div class="form-item w-100">
                    <label class="form-label my-3">Last Name<sup>*</sup></label>
                    <input type="text" class="form-control">
                </div>
            </div>
        </div>
        <div class="form-item">
            <label class="form-label my-3">Company Name<sup>*</sup></label>
            <input type="text" class="form-control">
        </div>
        <div class="form-item">
            <label class="form-label my-3">Address <sup>*</sup></label>
            <input type="text" class="form-control" placeholder="House Number Street Name">
        </div>
        <div class="form-item">
            <label class="form-label my-3">Town/City<sup>*</sup></label>
            <input type="text" class="form-control">
        </div>
        <div class="form-item">
            <label class="form-label my-3">Country<sup>*</sup></label>
            <input type="text" class="form-control">
        </div>
        <div class="form-item">
            <label class="form-label my-3">Postcode/Zip<sup>*</sup></label>
            <input type="text" class="form-control">
        </div>
        <div class="form-item">
            <label class="form-label my-3">Mobile<sup>*</sup></label>
            <input type="tel" class="form-control">
        </div>
        <div class="form-item">
            <label class="form-label my-3">Email Address<sup>*</sup></label>
            <input type="email" class="form-control">
        </div>
        <div class="form-check my-3">
            <input type="checkbox" class="form-check-input" id="Account-1" name="Accounts" value="Accounts">
            <label class="form-check-label" for="Account-1">Create an account?</label>
        </div>
        <hr>
        <div class="form-check my-3">
            <input class="form-check-input" type="checkbox" id="Address-1" name="Address" value="Address">
            <label class="form-check-label" for="Address-1">Ship to a different address?</label>
        </div>
        <div class="form-item">
            <textarea name="text" class="form-control" spellcheck="false" cols="30" rows="11" placeholder="Oreder Notes (Optional)"></textarea>
        </div>
    </div>
</template>

<style>
</style>