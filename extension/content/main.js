async function initPriceChart(advId) {
    try {
        const resp = await fetch('https://ct.kukite.com/mobile-bg/ads/' + advId),
            data = await resp.json(),
            $target = $('h1 + div + table[width="660"] > tbody > tr:nth-child(2) > td');
        $target.prepend('<div style="background: red;">hello world</div>');
    } catch (e) {
        console.warn('Extension failed to retrieve data:', e);
    }
}

$(() => {
    if (window.location.pathname === '/pcgi/mobile.cgi') {
        const params = new URLSearchParams(window.location.search);
        if (params.get('act') === '4') {
            initPriceChart(params.get('adv'));
        }
    }
});
