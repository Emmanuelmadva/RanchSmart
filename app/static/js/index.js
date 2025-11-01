

const sidebar = document.getElementById('sidebar')
const openButton = document.getElementById('open-sidebar-btn')
const toggleButton = document.getElementById('toggle-btn')
const overlay = document.getElementById('overlay')


function toggleSubMenu(button) {

    if (!button.nextElementSibling.classList.contains('show')) {
        closeAllSubMenus()
    }

    button.nextElementSibling.classList.toggle('show')
    button.classList.toggle('rotate')

    if (sidebar.classList.contains('close')) {
        sidebar.classList.toggle('close')
        toggleButton.classList.toggle('rotate')
    }
}

function closeAllSubMenus() {
    Array.from(sidebar.getElementsByClassName('show')).forEach(ul => {
        ul.classList.remove('show')
        ul.previousElementSibling.classList.remove('rotate')
    })
}


const media = window.matchMedia("(width < 750px)")


function toggleSidebar() {

    if (!media.matches) {
        console.log("C'est un desktop")
        sidebar.classList.toggle('close')
        toggleButton.classList.toggle('rotate')

        closeAllSubMenus()
        
    }else {
        console.log("C'est un smartphone")

        // if (sidebar.classList.contains('close')) {
        //     sidebar.classList.remove('close')
        // }
        closeSideBar()
    }

}

function openSideBar() {
    if (sidebar.classList.contains('close')) {
        sidebar.classList.remove('close')
    }
    sidebar.classList.add('show')
    overlay.classList.add('active')
    // openButton.setAttribute('aria-expanded', 'true')
    // sidebar.removeAttribute("inert")
}

function closeSideBar() {
    sidebar.classList.remove('show')
    overlay.classList.remove('active')
    // openButton.setAttribute('aria-expanded', 'false')
    // sidebar.setAttribute("inert", "")

}









