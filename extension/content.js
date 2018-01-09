function advFromMmm(mmm) {
    const url = new URL(mmm.href),
        search = new URLSearchParams(url.search);
    return search.get('adv');
}

function formatPrice(priceWithCurrency) {
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

function computeAdStats(adData) {
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

function initChartjs($canvas, adData, adStats) {
    const prices = adStats.filteredUpdates.map(u => u.price),
        dates = adStats.filteredUpdates.map(u => new Date(u.date)),
        chart = new Chart($canvas[0].getContext('2d'), {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Price',
                        data: prices,
                        steppedLine: 'before',
                    },
                ],
            },
            options: {
                legend: {
                    display: false,
                },
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            displayFormats: {
                                day: 'DD/MM',
                            },
                            unit: 'day',
                        },
                    }],
                    yAxes: [{
                        ticks: {
                            suggestedMin: Math.min(...prices) - 500,
                            suggestedMax: Math.max(...prices) + 500,
                        },
                    }],
                },
            },
        });
}

async function initAdInfo(advId) {
    let resp;
    try {
        resp = await fetch('https://ct.kukite.com/mobile-bg/ads/' + advId);
    } catch (e) {
        console.warn('Extension failed to retrieve data:', e);
        return;
    }
    const adData = await resp.json(),
        adStats = computeAdStats(adData),
        $canvas = $('<canvas>').attr('width', 344).attr('height', 180),
        $container = $('<div>').attr('id', 'car-tracker-price-chart').append($canvas);
    $('h1 ~ table[width="660"] > tbody > tr:nth-child(2) > td').prepend($container);
    initChartjs($canvas, adData, adStats);
}

async function initAdsListInfo() {
    let advs = $('.mmm').map((i, e) => advFromMmm(e)).toArray();

    const resp = await fetch('https://ct.kukite.com/mobile-bg/ads/?' +
        $.param({advs: advs.join(',')})),
        adsData = await resp.json();

    function createInfoCol(column, header, text) {
        return [
            $('<div>').css('grid-column', column).addClass('info-cell-header').text(header),
            $('<div>').css('grid-column', column).addClass('info-cell-text').text(text),
        ];
    }

    $('.mmm').each(function(i, e) {
        const $e = $(e),
            $trBefore = $e.closest('tr').next().next(),
            grid = $('<div>').addClass('ads-list-info-container'),
            adData = adsData[advFromMmm(e)];
        if (adData) {
            const adStats = computeAdStats(adData);
            grid.append(createInfoCol('1', 'Добавено', moment(
                adStats.firstUpdate.date).fromNow()));
            grid.append(createInfoCol('2', 'Макс. цена', formatPrice(adStats.maxPrice)));
            grid.append(createInfoCol('3', 'Мин. цена', formatPrice(adStats.minPrice)));
            grid.append(createInfoCol('4', 'Промени (последна)', adStats.lastPriceChange ?
                (adStats.priceChangeUpdates.length + '(' +
                    moment(adStats.lastPriceChange.date).fromNow()) + ')' : '-'
            ));

            $trBefore.after($('<tr>').append(
                $('<td>').attr('colspan', 5).append(grid),
            ));
        }
    });
}


$(() => {
    moment.locale('bg-BG');
    if (window.location.pathname === '/pcgi/mobile.cgi') {
        const params = new URLSearchParams(window.location.search);
        if (params.get('act') === '3') {
            initAdsListInfo();
        } else if (params.get('act') === '4') {
            initAdInfo(params.get('adv'));
        }
    }
});
