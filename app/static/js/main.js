// 购物车数量更新
function updateCartQuantity(itemId, action) {
    $.post('/update_cart', {
        item_id: itemId,
        action: action
    })
    .done(function(response) {
        if (response.status === 'success') {
            location.reload();
        }
    })
    .fail(function() {
        alert('更新失败，请重试！');
    });
}

// 添加到购物车
function addToCart(productId, quantity = 1, isRecommended = false) {
    $.post('/add_to_cart', {
        product_id: productId,
        quantity: quantity,
        is_recommended: isRecommended
    })
    .done(function(response) {
        if (response.status === 'success') {
            alert('商品已添加到购物车！');
        }
    })
    .fail(function() {
        alert('添加失败，请重试！');
    });
}

// 记录用户行为
function trackBehavior(productId, behaviorType, duration = null) {
    $.ajax({
        url: '/track_behavior',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            product_id: productId,
            behavior_type: behaviorType,
            duration: duration
        })
    });
}

// 页面加载完成后执行
$(document).ready(function() {
    // 添加到购物车按钮点击事件
    $('.add-to-cart').click(function() {
        const productId = $(this).data('product-id');
        const isRecommended = $(this).data('recommended') || false;
        addToCart(productId, 1, isRecommended);
    });
    
    // 更新购物车数量按钮点击事件
    $('.update-quantity').click(function() {
        const itemId = $(this).data('item-id');
        const action = $(this).data('action');
        updateCartQuantity(itemId, action);
    });
    
    // 记录页面访问时间
    let startTime = new Date();
    $(window).on('beforeunload', function() {
        let endTime = new Date();
        let duration = Math.round((endTime - startTime) / 1000);
        const productId = $('meta[name="product-id"]').attr('content');
        if (productId) {
            trackBehavior(productId, 'view', duration);
        }
    });
}); 