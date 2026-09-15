// OAK PRINT STUDIO - Interactive Storefront Logic

document.addEventListener('DOMContentLoaded', () => {
  initLucideIcons();
  initCategoryFilters();
  initProductConfigurator();
  initProductZoomLightbox();
  initCartDrawer();
});

function initLucideIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// 1. Home Page Category Filtering
function initCategoryFilters() {
  const filterButtons = document.querySelectorAll('.filter-btn');
  const productCards = document.querySelectorAll('.product-card');

  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');
      productCards.forEach(card => {
        const aesthetic = card.getAttribute('data-aesthetic') || '';
        if (filter === 'all' || aesthetic.toLowerCase().includes(filter.toLowerCase())) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

// 2. Product Page Interactive Configurator
function initProductConfigurator() {
  if (!window.PRODUCT_DATA) return;

  const product = window.PRODUCT_DATA;
  const mainImg = document.getElementById('main-view-image');
  const viewPillText = document.getElementById('view-mode-text');
  const thumbBtns = document.querySelectorAll('.thumb-btn');
  
  const frameBtns = document.querySelectorAll('.frame-opt-btn');
  const frameLabelSpan = document.getElementById('selected-frame-label');
  const sizeSelector = document.getElementById('size-selector');
  const priceDisplay = document.getElementById('dynamic-price');
  const skuDisplay = document.getElementById('current-sku-display');
  const directCheckoutBtn = document.getElementById('direct-stripe-checkout-btn');
  const addToBagBtn = document.getElementById('add-to-bag-btn');

  let currentFrame = 'natural_oak';
  let currentSize = sizeSelector ? sizeSelector.value : '24x36_in';
  let currentViewMode = 'framed'; // 'framed', 'corner', 'living_room'

  function getFramedDetailSrc(frameKey) {
    if (product.images.framed_detail_frames && product.images.framed_detail_frames[frameKey]) {
      return product.images.framed_detail_frames[frameKey];
    }
    return product.images.framed_product;
  }

  function getCornerDetailSrc(frameKey) {
    if (product.images.corner_detail_frames && product.images.corner_detail_frames[frameKey]) {
      return product.images.corner_detail_frames[frameKey];
    }
    return product.images.corner || product.images.hero;
  }

  function getLivingRoomSrc(frameKey) {
    if (product.images.living_room_frames && product.images.living_room_frames[frameKey]) {
      return product.images.living_room_frames[frameKey];
    }
    return product.images.living_room || product.images.hero;
  }

  function updateMainImageSrc(newSrc, label) {
    if (mainImg && newSrc) {
      mainImg.style.opacity = '0.4';
      setTimeout(() => {
        mainImg.src = newSrc;
        mainImg.style.opacity = '1';
      }, 120);
    }
    if (viewPillText && label) viewPillText.textContent = label;
  }

  // Thumbnail Switcher
  thumbBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      thumbBtns.forEach(b => {
        b.classList.remove('active');
        b.classList.remove('border-2', 'border-[#1C1C1E]');
        b.classList.add('border', 'border-[#E8E3DA]');
      });
      btn.classList.add('active');
      btn.classList.remove('border', 'border-[#E8E3DA]');
      btn.classList.add('border-2', 'border-[#1C1C1E]');

      currentViewMode = btn.getAttribute('data-view') || 'framed';
      const label = btn.getAttribute('data-label');
      let src = btn.getAttribute('data-src');

      if (currentViewMode === 'framed') {
        src = getFramedDetailSrc(currentFrame);
      } else if (currentViewMode === 'corner') {
        src = getCornerDetailSrc(currentFrame);
      } else if (currentViewMode === 'living_room') {
        src = getLivingRoomSrc(currentFrame);
      }

      updateMainImageSrc(src, label);
    });
  });

  // Frame Style Picker (Dynamically updates the frame color on all 3 views)
  frameBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      frameBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFrame = btn.getAttribute('data-frame');
      const label = btn.getAttribute('data-label');
      if (frameLabelSpan) frameLabelSpan.textContent = label;

      // Update thumbnail preview images
      const thumbFd = document.getElementById('thumb-framed-product');
      if (thumbFd) {
        const fdImg = thumbFd.querySelector('img');
        if (fdImg) fdImg.src = getFramedDetailSrc(currentFrame);
      }
      const thumbCorner = document.getElementById('thumb-corner');
      if (thumbCorner) {
        const cornerImg = thumbCorner.querySelector('img');
        if (cornerImg) cornerImg.src = getCornerDetailSrc(currentFrame);
      }
      const thumbLr = document.getElementById('thumb-living-room');
      if (thumbLr) {
        const lrImg = thumbLr.querySelector('img');
        if (lrImg) lrImg.src = getLivingRoomSrc(currentFrame);
      }

      // If user is currently looking at any of the 3 views, change the image live!
      if (currentViewMode === 'framed') {
        updateMainImageSrc(getFramedDetailSrc(currentFrame), `Framed Studio Close-up (${label})`);
      } else if (currentViewMode === 'corner') {
        updateMainImageSrc(getCornerDetailSrc(currentFrame), `45º Perspective (${label})`);
      } else if (currentViewMode === 'living_room') {
        updateMainImageSrc(getLivingRoomSrc(currentFrame), `Custom Staged Scene (${label})`);
      }

      updatePricingAndSku();
    });
  });



  // Size Picker Change
  if (sizeSelector) {
    sizeSelector.addEventListener('change', () => {
      currentSize = sizeSelector.value;
      updatePricingAndSku();
    });
  }

  function switchThumbnail(src, label) {
    if (mainImg) mainImg.src = src;
    if (viewPillText) viewPillText.textContent = label;
    thumbBtns.forEach(b => {
      if (b.getAttribute('data-src') === src) b.classList.add('active');
      else b.classList.remove('active');
    });
  }

  function getSelectedVariant() {
    // Find matching variant from catalog
    let matched = product.variants.find(v => v.frame_type === currentFrame && v.size === currentSize);
    if (!matched) {
      // Fallback to same size or first
      matched = product.variants.find(v => v.size === currentSize) || product.variants[0];
    }
    return matched;
  }

  function updatePricingAndSku() {
    const variant = getSelectedVariant();
    if (variant) {
      if (priceDisplay) priceDisplay.textContent = `$${variant.retail_price.toFixed(2)}`;
      if (skuDisplay) skuDisplay.textContent = variant.gelato_sku;
    }
  }

  const appleGooglePayBtn = document.getElementById('apple-google-pay-btn');

  async function triggerCheckout(btnElement, loadingText) {
    const variant = getSelectedVariant();
    const originalHtml = btnElement.innerHTML;
    btnElement.innerHTML = `<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i><span>${loadingText}</span>`;
    initLucideIcons();

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: [{
            product_id: product.id,
            product_title: product.title,
            variant_id: variant.variant_id,
            size_label: variant.size_label,
            frame_label: variant.frame_label,
            gelato_sku: variant.gelato_sku,
            price: variant.retail_price,
            image_url: product.images.hero,
            quantity: 1
          }]
        })
      });

      const data = await response.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert('Error initializing checkout. Please try again.');
        btnElement.innerHTML = originalHtml;
      }
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Network error. Redirecting to local test order...');
      window.location.href = `/success?order_ref=order_${Date.now()}`;
    }
  }

  // Apple Pay / Google Pay Direct 1-Click Buy
  if (appleGooglePayBtn) {
    appleGooglePayBtn.addEventListener('click', () => {
      triggerCheckout(appleGooglePayBtn, 'Opening Apple Pay / Google Pay...');
    });
  }

  // Direct Card Express Checkout
  if (directCheckoutBtn) {
    directCheckoutBtn.addEventListener('click', () => {
      triggerCheckout(directCheckoutBtn, 'Connecting to Stripe...');
    });
  }


  // Add to Bag Button
  if (addToBagBtn) {
    addToBagBtn.addEventListener('click', () => {
      const variant = getSelectedVariant();
      Cart.addItem({
        product_id: product.id,
        product_title: product.title,
        variant_id: variant.variant_id,
        size_label: variant.size_label,
        frame_label: variant.frame_label,
        gelato_sku: variant.gelato_sku,
        price: variant.retail_price,
        image_url: product.images.hero,
        quantity: 1
      });
      openCartDrawer();
    });
  }

  // Initial calculation
  updatePricingAndSku();
}

// 3. Slide-Out Shopping Bag Drawer & State Management
const Cart = {
  get items() {
    return JSON.parse(localStorage.getItem('oakprintstudio_cart') || localStorage.getItem('atelier_cart') || '[]');
  },
  set items(val) {
    localStorage.setItem('oakprintstudio_cart', JSON.stringify(val));
    updateCartUI();
  },
  addItem(newItem) {
    const list = this.items;
    const existing = list.find(i => i.product_id === newItem.product_id && i.variant_id === newItem.variant_id);
    if (existing) {
      existing.quantity += 1;
    } else {
      list.push(newItem);
    }
    this.items = list;
    if (window.pintrk) {
      window.pintrk('track', 'addtocart', {
        value: newItem.price,
        order_quantity: 1,
        currency: 'USD',
        product_id: newItem.product_id
      });
    }
  },
  removeItem(index) {
    const list = this.items;
    list.splice(index, 1);
    this.items = list;
  },
  clear() {
    this.items = [];
  }
};

function initCartDrawer() {
  const openBtn = document.getElementById('open-cart-btn');
  const closeBtn = document.getElementById('close-cart-btn');
  const backdrop = document.getElementById('cart-backdrop');
  const checkoutBtn = document.getElementById('cart-checkout-btn');

  if (openBtn) openBtn.addEventListener('click', openCartDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeCartDrawer);
  if (backdrop) backdrop.addEventListener('click', closeCartDrawer);

  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', async () => {
      const items = Cart.items;
      if (items.length === 0) return;

      checkoutBtn.innerText = 'Connecting to Stripe...';
      try {
        const res = await fetch('/api/checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items })
        });
        const data = await res.json();
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } catch (e) {
        window.location.href = `/success?order_ref=order_${Date.now()}`;
      }
    });
  }

  updateCartUI();
}

function openCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  if (drawer) drawer.classList.remove('hidden');
}

function closeCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  if (drawer) drawer.classList.add('hidden');
}

function updateCartUI() {
  const items = Cart.items;
  const badge = document.getElementById('cart-count-badge');
  const container = document.getElementById('cart-items-container');
  const rawSubtotalEl = document.getElementById('cart-raw-subtotal');
  const discountRow = document.getElementById('cart-discount-row');
  const discountLabel = document.getElementById('cart-discount-label');
  const discountVal = document.getElementById('cart-discount-val');
  const subtotalEl = document.getElementById('cart-subtotal-price');

  const progressMsg = document.getElementById('bundle-progress-msg');
  const tierTag = document.getElementById('bundle-tier-tag');
  const progressBar = document.getElementById('bundle-progress-bar');

  const totalCount = items.reduce((sum, i) => sum + i.quantity, 0);
  const rawSubtotal = items.reduce((sum, i) => sum + (i.price * i.quantity), 0);

  // Bundle Discount Calculation
  let discountRate = 0.0;
  let discountName = '';

  if (totalCount >= 3) {
    discountRate = 0.20; // 20% off for 3+ items
    discountName = 'Gallery Triptych Bundle (20% Off)';
    if (progressMsg) progressMsg.textContent = '🎉 Unlocked Maximum 20% Gallery Bundle Savings!';
    if (tierTag) tierTag.textContent = 'Tier 3 (Max)';
    if (progressBar) {
      progressBar.style.width = '100%';
      progressBar.classList.replace('bg-[#C66B4D]', 'bg-[#3B7A57]');
    }
  } else if (totalCount === 2) {
    discountRate = 0.15; // 15% off for 2 items
    discountName = 'Gallery Pair Bundle (15% Off)';
    if (progressMsg) progressMsg.textContent = '✨ Add 1 more print to unlock 20% savings!';
    if (tierTag) tierTag.textContent = 'Tier 2 (15% Off)';
    if (progressBar) {
      progressBar.style.width = '66%';
      progressBar.classList.replace('bg-[#3B7A57]', 'bg-[#C66B4D]');
    }
  } else if (totalCount === 1) {
    if (progressMsg) progressMsg.textContent = 'Add 1 more print to unlock 15% bundle savings!';
    if (tierTag) tierTag.textContent = 'Tier 1';
    if (progressBar) {
      progressBar.style.width = '33%';
      progressBar.classList.replace('bg-[#3B7A57]', 'bg-[#C66B4D]');
    }
  } else {
    if (progressMsg) progressMsg.textContent = 'Add 2 prints to unlock 15% bundle savings!';
    if (tierTag) tierTag.textContent = 'Tier 0';
    if (progressBar) progressBar.style.width = '0%';
  }

  const discountAmount = rawSubtotal * discountRate;
  const finalTotal = rawSubtotal - discountAmount;

  if (badge) badge.textContent = totalCount;
  if (rawSubtotalEl) rawSubtotalEl.textContent = `$${rawSubtotal.toFixed(2)}`;

  if (discountRow && discountVal && discountLabel) {
    if (discountAmount > 0) {
      discountRow.classList.remove('hidden');
      discountLabel.textContent = discountName;
      discountVal.textContent = `-$${discountAmount.toFixed(2)}`;
    } else {
      discountRow.classList.add('hidden');
    }
  }

  if (subtotalEl) subtotalEl.textContent = `$${finalTotal.toFixed(2)}`;

  if (container) {
    if (items.length === 0) {
      container.innerHTML = `<div class="text-center text-[#7A756D] py-16">Your bag is currently empty.</div>`;
    } else {
      container.innerHTML = items.map((item, idx) => `
        <div class="flex items-center gap-4 bg-white p-3 rounded-lg border border-[#E8E3DA]">
          <img src="${item.image_url}" class="w-16 h-16 object-cover rounded border border-[#E8E3DA]">
          <div class="flex-grow text-xs">
            <h4 class="font-bold text-[#1C1C1E] text-sm">${item.product_title}</h4>
            <p class="text-[#7A756D]">${item.frame_label}</p>
            <p class="text-[#7A756D]">${item.size_label}</p>
            <span class="font-bold text-[#1C1C1E] mt-1 block">$${item.price.toFixed(2)} × ${item.quantity}</span>
          </div>
          <button onclick="Cart.removeItem(${idx})" class="text-red-400 hover:text-red-600 p-1 text-xs">
            Remove
          </button>
        </div>
      `).join('');
    }
  }
}

// 5. High-Resolution Interactive Zoom & Lightbox
function initProductZoomLightbox() {
  const mainContainer = document.getElementById('main-view-container');
  const mainImg = document.getElementById('main-view-image');
  const modal = document.getElementById('zoom-lightbox-modal');
  const modalImg = document.getElementById('modal-zoom-image');
  const modalStage = document.getElementById('modal-zoom-stage');
  const modalViewport = document.getElementById('modal-zoom-viewport');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalZoomToggleBtn = document.getElementById('modal-zoom-toggle-btn');
  const modalZoomText = document.getElementById('modal-zoom-text');
  const modalZoomIcon = document.getElementById('modal-zoom-icon');
  const modalViewLabel = document.getElementById('modal-view-label');
  const modalThumbBtns = document.querySelectorAll('.modal-thumb-btn');

  if (!mainContainer || !modal || !modalImg || !modalStage || !modalViewport) return;

  let isZoomed = false;
  const ZOOM_SCALE = 2.4;

  function openModal() {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    setTimeout(() => {
      modal.classList.remove('opacity-0');
      modal.classList.add('opacity-100');
    }, 10);

    // Sync modal image with current main image
    if (mainImg) {
      modalImg.src = mainImg.src;
    }
    const viewText = document.getElementById('view-mode-text');
    if (viewText && modalViewLabel) {
      modalViewLabel.textContent = viewText.textContent;
    }

    // Sync active modal thumbnail with page thumbnail
    const activePageThumb = document.querySelector('.thumb-btn.active');
    const activeView = activePageThumb ? activePageThumb.getAttribute('data-view') : 'framed';
    modalThumbBtns.forEach(btn => {
      if (btn.getAttribute('data-view') === activeView) {
        btn.classList.add('active', 'border-2', 'border-[#B8834E]');
        btn.classList.remove('border-white/30');
      } else {
        btn.classList.remove('active', 'border-2', 'border-[#B8834E]');
        btn.classList.add('border', 'border-white/30');
      }
    });

    resetZoom();
    document.body.style.overflow = 'hidden';
    if (window.lucide) window.lucide.createIcons();
  }

  function closeModal() {
    modal.classList.remove('opacity-100');
    modal.classList.add('opacity-0');
    setTimeout(() => {
      modal.classList.remove('flex');
      modal.classList.add('hidden');
      resetZoom();
      document.body.style.overflow = '';
    }, 250);
  }

  function setZoom(zoomed) {
    isZoomed = zoomed;
    if (isZoomed) {
      modalViewport.classList.remove('cursor-zoom-in');
      modalViewport.classList.add('cursor-zoom-out');
      if (modalZoomText) modalZoomText.textContent = 'Reset (1.0x)';
      if (modalZoomIcon) modalZoomIcon.setAttribute('data-lucide', 'zoom-out');
    } else {
      resetZoom();
    }
    if (window.lucide) window.lucide.createIcons();
  }

  function resetZoom() {
    isZoomed = false;
    modalViewport.classList.remove('cursor-zoom-out');
    modalViewport.classList.add('cursor-zoom-in');
    modalStage.style.transform = 'translate(0px, 0px) scale(1)';
    if (modalZoomText) modalZoomText.textContent = 'Zoom In (2.5x)';
    if (modalZoomIcon) modalZoomIcon.setAttribute('data-lucide', 'zoom-in');
  }

  // Mouse pan when zoomed
  modalViewport.addEventListener('mousemove', (e) => {
    if (!isZoomed) return;
    const rect = modalViewport.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width; // 0 to 1
    const y = (e.clientY - rect.top) / rect.height; // 0 to 1

    const panX = (0.5 - x) * (rect.width * 0.95);
    const panY = (0.5 - y) * (rect.height * 0.95);

    modalStage.style.transform = `translate(${panX}px, ${panY}px) scale(${ZOOM_SCALE})`;
  });

  // Toggle zoom on image click
  modalViewport.addEventListener('click', (e) => {
    if (e.target.closest('#modal-zoom-toggle-btn') || e.target.closest('#modal-close-btn') || e.target.closest('.modal-thumb-btn')) {
      return;
    }
    setZoom(!isZoomed);
  });

  // Zoom button click
  if (modalZoomToggleBtn) {
    modalZoomToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      setZoom(!isZoomed);
    });
  }

  // Open modal trigger on main container
  mainContainer.addEventListener('click', openModal);

  // Close modal button
  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (modal.classList.contains('hidden')) return;
    if (e.key === 'Escape') closeModal();
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      setZoom(!isZoomed);
    }
  });

  // Modal thumbnail switching
  modalThumbBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      modalThumbBtns.forEach(b => {
        b.classList.remove('active', 'border-2', 'border-[#B8834E]');
        b.classList.add('border', 'border-white/30');
      });
      btn.classList.add('active', 'border-2', 'border-[#B8834E]');
      btn.classList.remove('border-white/30');

      const view = btn.getAttribute('data-view');
      const label = btn.getAttribute('data-label');
      
      const targetPageThumb = document.querySelector(`.thumb-btn[data-view="${view}"]`);
      if (targetPageThumb) {
        targetPageThumb.click();
        setTimeout(() => {
          if (mainImg) modalImg.src = mainImg.src;
        }, 130);
      } else if (btn.getAttribute('data-src')) {
        modalImg.src = btn.getAttribute('data-src');
      }

      if (modalViewLabel && label) modalViewLabel.textContent = label;
      resetZoom();
    });
  });
}

