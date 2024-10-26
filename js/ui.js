function getOfferTypeBadge(offer) {
    let type = 'CPI';
    if (offer.type) {
        type = offer.type.toUpperCase();
    } else if (offer.name.includes('PIN')) {
        type = 'PIN';
    } else if (offer.name.includes('VID')) {
        type = 'VID';
    } else if (offer.name.includes('CPA')) {
        type = 'CPA';
    }
    
    return `<span class="offer-type-badge offer-type-${type.toLowerCase()}">${type}</span>`;
}

function generateOfferHtml(offer) {
    return `
        <div class="app mt-4" data-offer-id="${offer.offerid}" data-redirect="${offer.link}">
            ${getOfferTypeBadge(offer)}
            <div class="incentive">Free</div>
            <div class="row align-items-center">
                <div class="col-3">
                    <img class="img-fluid offer-image" src="${offer.picture}" alt="${offer.name_short}">
                </div>
                <div class="col-8">
                    <p class="name mb-0 fs-6 text-start fw-medium">${offer.name_short}</p>
                    <p class="description mb-0 mt-1 fs-xs fw-normal text-start">${offer.adcopy}</p>
                </div>
                <div class="col-1">
                    <i class="bi bi-chevron-right float-end fs-6" style="color:rgb(169, 169, 202);"></i>
                </div>
            </div>
        </div>
    `;
}

async function renderOffers(offers) {
    const offersContainer = document.getElementById('offers-container');

    if (offers.length === 0) {
        offersContainer.innerHTML = `
            <div class="text-white">
                No offers available at this time. Please try again later.
            </div>
        `;
        return;
    }

    offersContainer.innerHTML = offers
        .map(offer => generateOfferHtml(offer))
        .join('');

    document.querySelectorAll('.app').forEach(item => {
        item.addEventListener('click', () => {
            const offerId = item.dataset.offerId;
            const redirectUrl = item.dataset.redirect;
            
            document.dispatchEvent(new CustomEvent('offer-click', { 
                detail: {
                    offerId,
                    redirectUrl
                }
            }));

            window.location.href = redirectUrl;
        });
    });
}

export { renderOffers };