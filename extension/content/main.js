function initPriceChart(advId) {
    fetch('http://ct.kukite.com/mobile-bg/ads/' + advId).then(resp => {
        console.log('resp', resp.data);
    }).catch(e => {
    });
}

$(() => {
    if (window.location.pathname === '/pcgi/mobile.cgi') {
        const params = new URLSearchParams(window.location.search);
        if (params.get('act') === '4') {
            initPriceChart(params.get('adv'));
        }
    }
});
