const log = document.getElementById('cont')
let x_off = log.offsetWidth
let x = window.innerWidth
let y = window.innerHeight

console.log(x_off)

log.style.position = 'absolute'
log.style.left = (x/2) - (x_off/2) + 'px'
log.style.top = (y/4) + 'px'

setInterval(function () {
    x = window.innerWidth
    y = window.innerHeight
    log.style.position = 'absolute'
    log.style.left = (x/2) - (x_off/2) + 'px'
    log.style.top = (y/4) + 'px'
}, 100)
