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

function getMinMaxPrice(activeUpdates) {
    let minPrice = null, maxPrice = null;
    for (let update of activeUpdates) {
        if (update.price === -1) {
            continue;
        }
        const p = {
            price: update.price,
            currency: update.price_currency,
        };
        if (minPrice === null || update.price < minPrice.price) {
            minPrice = p;
        }
        if (maxPrice === null || update.price > maxPrice.price) {
            maxPrice = p;
        }
    }
    return {
        minPrice: minPrice,
        maxPrice: maxPrice,
    }
}

function getFilteredUpdates(activeUpdates) {
    let filtered = [];
    if (activeUpdates.length >= 1) {
        filtered.push(activeUpdates[0]);
        for (let update of activeUpdates) {
            if (update.price !== filtered[filtered.length - 1].price) {
                filtered.push(update);
            }
        }

        let lastUpdate = activeUpdates[activeUpdates.length - 1];
        let lastFiltered = filtered[filtered.length - 1];
        if (lastUpdate.date !== lastFiltered.data) {
            filtered.push(lastUpdate);
        }
    }
    return filtered;
}

function getPriceChangeUpdates(activeUpdates) {
    let price = null,
        changes = [];
    for (let update of activeUpdates) {
        if (update.price !== price) {
            if (price !== null) {
                changes.push(update);
            }
            price = update.price;
        }
    }
    return changes;
}

export function computeAdStats(adData) {
    const updates = [].concat(adData.updates),
        activeUpdates = updates.filter(u => u.active),
        priceChangeUpdates = getPriceChangeUpdates(activeUpdates),
        result = {
            updates: updates,
            activeUpdates: activeUpdates,
            filteredUpdates: getFilteredUpdates(activeUpdates),
            priceChangeUpdates: priceChangeUpdates,

            firstUpdate: updates[0],
            lastUpdate: updates[updates.length - 1],
            lastPriceChange: priceChangeUpdates.length ?
                priceChangeUpdates[priceChangeUpdates.length - 1] : null,
            lastActiveUpdate: null,

            minPrice: null,
            maxPrice: null,
        };
    Object.assign(result, getMinMaxPrice(result.activeUpdates));
    if (activeUpdates.length) {
        result.lastActiveUpdate = activeUpdates[activeUpdates.length - 1];
    }
    return result;
}
