import { storeAPI } from '@/utils/api'

// 在組件中使用
async fetchProducts() {
    try {
        const response = await storeAPI.getProducts({
            page: this.currentPage,
            pageSize: this.pageSize,
            category: this.selectedCategory,
            brand: this.selectedBrand,
            series: this.selectedSeries,
            minPrice: this.minPrice,
            maxPrice: this.maxPrice,
            sort: this.sortBy
        })
        this.products = response.results
        this.totalPages = Math.ceil(response.count / this.pageSize)
    } catch (error) {
        console.error('獲取商品列表失敗：', error)
        // 處理錯誤...
    }
} 