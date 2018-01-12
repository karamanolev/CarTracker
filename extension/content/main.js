import {advFromMmm, computeAdStats, formatPrice} from './utils.js';

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
                            tooltipFormat: {
                                day: 'DD/MM',
                            },
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

function getAdsInfoContainer(adStats) {
    function createInfoCol(column, header, text) {
        return [
            $('<div>').css('grid-column', column).addClass('info-cell-header').text(header),
            $('<div>').css('grid-column', column).addClass('info-cell-text').text(text),
        ];
    }

    const grid = $('<div>').addClass('ads-list-info-container');
    grid.append(createInfoCol('1', 'Добавено', moment(
        adStats.firstUpdate.date).fromNow()));
    grid.append(createInfoCol('2', 'Макс. цена', formatPrice(adStats.maxPrice)));
    grid.append(createInfoCol('3', 'Мин. цена', formatPrice(adStats.minPrice)));
    grid.append(createInfoCol('4', 'Промени (последна)', adStats.lastPriceChange ?
        (adStats.priceChangeUpdates.length + ' (' +
            moment(adStats.lastPriceChange.date).fromNow()) + ')' : '-'
    ));
    return grid;
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
        $grid = getAdsInfoContainer(adStats),
        $container = $('<div>').attr('id', 'car-tracker-price-chart').append($canvas, $grid);
    $('h1 ~ table[width="660"] > tbody > tr:nth-child(2) > td').prepend($container);
    initChartjs($canvas, adData, adStats);
}

async function initAdsListInfo() {
    let advs = $('.mmm').map((i, e) => advFromMmm(e)).toArray();

    const resp = await fetch('https://ct.kukite.com/mobile-bg/ads/?' +
        $.param({advs: advs.join(',')})),
        adsData = await resp.json();

    $('.mmm').each(function(i, e) {
        const $e = $(e),
            $trBefore = $e.closest('tr').next().next(),
            adData = adsData[advFromMmm(e)];
        if (adData) {
            const adStats = computeAdStats(adData),
                grid = getAdsInfoContainer(adStats);

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
