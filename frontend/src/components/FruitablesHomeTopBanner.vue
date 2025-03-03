<script setup>
</script>

<template>
<!-- 首頁頂端Banner Component (FruitablesHomeTopBanner.vue)-->
<div class="父組件highlight">
  <!-- Modal Search Start -->
  <div
    class="modal fade"
    id="searchModal"
    tabindex="-1"
    aria-labelledby="exampleModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content rounded-0">
        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabel">Search by keyword</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body d-flex align-items-center">
          <div class="input-group w-75 mx-auto d-flex">
            <input
              type="search"
              class="form-control p-3"
              placeholder="keywords"
              aria-describedby="search-icon-1"
            />
            <span id="search-icon-1" class="input-group-text p-3"
              ><i class="fa fa-search"></i
            ></span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal Search End -->

  <!-- Hero Start -->
  <div class="container-fluid py-5 mb-5 hero-header">
    <div class="container py-5">
      <div class="row g-5 align-items-center">
        <div class="col-md-12 col-lg-7">
          <h4 class="mb-3 text-secondary">✧ Welcome to ACGN 綜合論壇 ✧</h4>
          <h1 class="mb-5 display-3 text-primary">
            ACGN的交流與分享
          </h1>
          <div class="position-relative mx-auto">
            <input
              class="form-control border-2 border-secondary w-75 py-3 px-4 rounded-pill"
              type="number"
              placeholder="搜尋 遊戲、動畫、電影相關..."
            />
            <button
              type="submit"
              class="btn btn-primary border-2 border-secondary py-3 px-4 position-absolute rounded-pill text-white h-100"
              style="top: 0; right: 25%"
            >
              立即搜尋
            </button>
          </div>
        </div>
        <div class="col-md-12 col-lg-5">
          <div
            id="carouselId"
            class="carousel slide position-relative"
            data-bs-ride="carousel"
          >
            <div class="carousel-inner" role="listbox">
              <div class="carousel-item active rounded">
                <img
                  src="https://p2.bahamut.com.tw/B/ACG/c/47/0000136647.JPG"
                  class="img-fluid w-100 h-100 bg-secondary rounded"
                  alt="First slide"
                />
                <a href="#" class="btn px-4 py-2 text-white rounded">動畫 Anime</a>
              </div>
              <div class="carousel-item rounded">
                <img
                  src="https://p-cdnstatic.svc.litv.tv/pics/9045-000000-025783.jpg"
                  class="img-fluid w-100 h-100 rounded"
                  alt="Second slide"
                />
                <a href="#" class="btn px-4 py-2 text-white rounded"
                  >電影 Movie</a
                >
              </div>
              <div class="carousel-item rounded">
                <img
                  src="http://localhost:5173/images/games/%E4%B8%96%E7%BA%AA%E4%B9%8B%E7%9F%B32.jpg"
                  class="img-fluid w-100 h-100 rounded"
                  alt="Second slide"
                />
                <a href="#" class="btn px-4 py-2 text-white rounded"
                  >遊戲 Game</a
                >
              </div>
            </div>
            <button
              class="carousel-control-prev"
              type="button"
              data-bs-target="#carouselId"
              data-bs-slide="prev"
            >
              <span
                class="carousel-control-prev-icon"
                aria-hidden="true"
              ></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button
              class="carousel-control-next"
              type="button"
              data-bs-target="#carouselId"
              data-bs-slide="next"
            >
              <span
                class="carousel-control-next-icon"
                aria-hidden="true"
              ></span>
              <span class="visually-hidden">Next</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Hero End -->
</div>
</template>

<style lang="css" scoped>
</style>
