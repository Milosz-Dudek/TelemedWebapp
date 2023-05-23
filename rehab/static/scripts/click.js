document.getElementsByTagName("html")[0].addEventListener('click', function(e){
    let x = e.clientX
    let y = e.clientY
    console.log(x,y)
    let ripples = document.createElement('span')
    ripples.classList.add("ripple")
    ripples.style.position = 'absolute'
    ripples.style.left = x + 'px'
    ripples.style.top = y + 'px'
    ripples.style.zIndex = 2
    this.appendChild(ripples)
    setTimeout(() =>{
        ripples.remove()
    },1000)
})