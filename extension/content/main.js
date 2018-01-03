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
                    }
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
                                day: 'DD/MM'
                            },
                            unit: 'day',
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            suggestedMin: Math.min(...prices) - 500,
                            suggestedMax: Math.max(...prices) + 500,
                        },
                    }],
                }
            }
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
    let advs = $('.mmm').map((i, e) => {
        const url = new URL(e.href),
            search = new URLSearchParams(url.search);
        return search.get('adv');
    }).toArray();

    let resp = await fetch('https://ct.kukite.com/mobile-bg/ads/?' +
        $.param({advs: advs.join(',')}));
    console.log(resp);

    function createInfoCol(column, header, text) {
        return [
            $('<div>').css('grid-column', column).css('grid-row', '1').text(header),
            $('<div>').css('grid-column', column).css('grid-row', '2').text(text),
        ];
    }

    $('.mmm').each(function(i, e) {
        const $e = $(e),
            $trBefore = $e.closest('tr').next().next(),
            grid = $('<div>').addClass('ads-list-info-container');
        grid.append(createInfoCol('1', 'Added', 'hello'));
        grid.append(createInfoCol('2', 'Start price', 'asdf'));
        $trBefore.after($('<tr>').append(
            $('<td>').attr('colspan', 5).append(grid)
        ));
    });
}


$(() => {
    if (window.location.pathname === '/pcgi/mobile.cgi') {
        const params = new URLSearchParams(window.location.search);
        if (params.get('act') === '3') {
            initAdsListInfo();
        } else if (params.get('act') === '4') {
            initAdInfo(params.get('adv'));
        }
    }
});
