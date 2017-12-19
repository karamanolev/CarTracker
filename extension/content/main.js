import {parseQueryString} from './utils.js';

function initPriceChart(advId) {
    alert('init price ' + advId);
}

$(() => {
    if (window.location.pathname === '/pcgi/mobile.cgi') {
        const params = parseQueryString(window.location.search);
        initPriceChart(params.adv);
    }
});
