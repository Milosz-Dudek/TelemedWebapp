const hours = document.getElementById('hours')
const minutes = document.getElementById('minutes')
const seconds = document.getElementById('seconds')
const dots = document.querySelectorAll('.dots')

var visibility = 1

setInterval(function(){
    var date = new Date()
    var h = date.getHours()
    var m = date.getMinutes()
    var s = date.getSeconds()
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

    dots.forEach(function(item,index){
        if(visibility == 1)
            item.innerHTML = ' '
        else if(visibility == 0)
            item.innerHTML = ':'
    })
    visibility = !visibility
},1000)