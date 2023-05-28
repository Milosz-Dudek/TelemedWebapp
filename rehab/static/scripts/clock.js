const hours = document.getElementById('hours')
const minutes = document.getElementById('minutes')
const seconds = document.getElementById('seconds')
const dots = document.querySelectorAll('.dots')

var visibility = 1
function get_date(hours,minutes,seconds){
    let date = new Date()
    let h = date.getHours()
    let m = date.getMinutes()
    let s = date.getSeconds()
    if(h < 10 )
        hours.innerHTML = '0' + h
    else
        hours.innerHTML = h
    if(m < 10 )
        minutes.innerHTML = '0' + m
    else
        minutes.innerHTML = m
    if(s < 10)
        seconds.innerHTML = '0' + s
    else
        seconds.innerHTML = s
}
setInterval(function(){
    get_date(hours,minutes,seconds)
    dots.forEach(function(item,index){
        if(visibility == 1)
            item.innerHTML = ' '
        else if(visibility == 0)
            item.innerHTML = ':'
    })
    visibility = !visibility
},1000)