import {advFromMmm, computeAdStats, formatPrice} from './utils.js';

function initChartjs(data) {
    const prices = data.updates.map(u => u.price),
        dates = data.updates.map(u => new Date(u.date)),
        chart = new Chart($('canvas')[0].getContext('2d'), {
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
    const data = await resp.json(),
        $target = $('h1 ~ table[width="660"] > tbody > tr:nth-child(2) > td'),
        $canvas = $('<canvas>'),
        $priceChart = $('<div>').attr('id', 'car-tracker-price-chart').append(
            $('<canvas>').attr('width', 344).attr('height', 180));
    $target.prepend($priceChart);
    initChartjs(data);
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
            const stats = computeAdStats(adData);
            grid.append(createInfoCol('1', 'Добавено', moment(
                stats.firstUpdate.date).fromNow()));
            grid.append(createInfoCol('2', 'Мин. цена', formatPrice(stats.minPrice)));
            grid.append(createInfoCol('3', 'Макс. цена', formatPrice(stats.maxPrice)));
            const lastPriceChange = stats.lastPriceChange ? moment(
                stats.lastPriceChange.date).fromNow() : '-';
            grid.append(createInfoCol('4', 'Последна промяна', lastPriceChange));

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
