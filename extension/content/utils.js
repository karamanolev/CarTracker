export function advFromMmm(mmm) {
    const url = new URL(mmm.href),
        search = new URLSearchParams(url.search);
    return search.get('adv');
}

export function formatPrice(priceWithCurrency) {
    if (priceWithCurrency === null) {
        return '-';
    }
    const p = priceWithCurrency.price.toFixed(2) + ' ',
        currency = priceWithCurrency.currency;
    if (currency === 0) {
        return p + ' лв.';
    } else if (currency === 1) {
        return p + ' EUR';
    } else if (currency === 2) {
        return '$' + p;
    } else {
        throw 'Unknown currency';
    }
}

export function computeAdStats(adData) {
    const updates = [].concat(adData.updates),
        activeUpdates = updates.filter(u => u.active),
        result = {
            updates: updates,
            firstUpdate: updates[0],
            lastUpdate: updates[updates.length - 1],
            lastPriceChange: null,
            lastActiveUpdate: null,
            minPrice: null,
            maxPrice: null,
        };
    for (let update of activeUpdates) {
        if (update.price === -1) {
            continue;
        }
        const p = {
            price: update.price,
            currency: update.price_currency,
        };
        if (result.minPrice === null || update.price < result.minPrice.price) {
            result.minPrice = p;
        }
        if (result.maxPrice === null || update.price > result.maxPrice.price) {
            result.maxPrice = p;
        }
    }
    if (activeUpdates.length) {
        result.lastActiveUpdate = activeUpdates[activeUpdates.length - 1];
    }
    for (let i = activeUpdates.length - 1; i >= 1; --i) {
        const u = activeUpdates[i],
            p = activeUpdates[i - 1];
        if (u.price !== p.price) {
            result.lastPriceChange = u;
            break;
        }
    }
    return result;
}
