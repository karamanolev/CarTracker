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

async function initPriceChart(advId) {
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

$(() => {
    if (window.location.pathname === '/pcgi/mobile.cgi') {
        const params = new URLSearchParams(window.location.search);
        if (params.get('act') === '4') {
            initPriceChart(params.get('adv'));
        }
    }
});
