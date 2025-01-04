<script setup>

</script>

<template>
    <!-- 發送評論 Component (FruitablesDetailReply.vue)-->
    <form action="#" class="父組件highlight">
        <h4 class="mb-5 fw-bold">Leave a Reply</h4>
        <div class="row g-4">
            <div class="col-lg-6">
                <div class="border-bottom rounded">
                    <input type="text" class="form-control border-0 me-4" placeholder="Yur Name *">
                </div>
            </div>
            <div class="col-lg-6">
                <div class="border-bottom rounded">
                    <input type="email" class="form-control border-0" placeholder="Your Email *">
                </div>
            </div>
            <div class="col-lg-12">
                <div class="border-bottom rounded my-4">
                    <textarea name="" id="" class="form-control border-0" cols="30" rows="8" placeholder="Your Review *" spellcheck="false"></textarea>
                </div>
            </div>
            <div class="col-lg-12">
                <div class="d-flex justify-content-between py-3 mb-5">
                    <div class="d-flex align-items-center">
                        <p class="mb-0 me-3">Please rate:</p>
                        <div class="d-flex align-items-center" style="font-size: 12px;">
                            <i class="fa fa-star text-muted"></i>
                            <i class="fa fa-star"></i>
                            <i class="fa fa-star"></i>
                            <i class="fa fa-star"></i>
                            <i class="fa fa-star"></i>
                        </div>
                    </div>
                    <a href="#" class="btn border border-secondary text-primary rounded-pill px-4 py-3"> Post Comment</a>
                </div>
            </div>
        </div>
    </form>
</template>

<style>
</style>