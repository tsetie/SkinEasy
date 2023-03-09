// const buttonleft1 = document.getElementById('leftarrow1');
// const buttonright1 = document.getElementById('rightarrow1');

// buttonleft1.onclick = function() {
//   document.getElementById('step1container').scrollLeft -= 505;
// };
// buttonright1.onclick = function() {
//   document.getElementById('step1container').scrollLeft += 505;
// };

// const buttonleft2 = document.getElementById('leftarrow2');
// const buttonright2 = document.getElementById('rightarrow2');

// buttonleft2.onclick = function() {
//   document.getElementById('step2container').scrollLeft -= 505;
// };
// buttonright2.onclick = function() {
//   document.getElementById('step2container').scrollLeft += 505;
// };

// const buttonleft3 = document.getElementById('leftarrow3');
// const buttonright3 = document.getElementById('rightarrow3');

// buttonleft3.onclick = function() {
//   document.getElementById('step3container').scrollLeft -= 505;
// };
// buttonright3.onclick = function() {
//   document.getElementById('step3container').scrollLeft += 505;
// };

// const buttonleft4 = document.getElementById('leftarrow4');
// const buttonright4 = document.getElementById('rightarrow4');

// buttonleft4.onclick = function() {
//   document.getElementById('step4container').scrollLeft -= 505;
// };
// buttonright4.onclick = function() {
//   document.getElementById('step4container').scrollLeft += 505;
// };

// const buttonleft5 = document.getElementById('leftarrow5');
// const buttonright5 = document.getElementById('rightarrow5');

// buttonleft5.onclick = function() {
//   document.getElementById('step5container').scrollLeft -= 505;
// };
// buttonright5.onclick = function() {
//   document.getElementById('step5container').scrollLeft += 505;
// };

// const buttonleft6 = document.getElementById('leftarrow6');
// const buttonright6 = document.getElementById('rightarrow6');

// buttonleft6.onclick = function() {
//   document.getElementById('step6container').scrollLeft -= 505;
// };
// buttonright6.onclick = function() {
//   document.getElementById('step6container').scrollLeft += 505;
// };





//////////////////////////////////////
// Add JS for custom click features //
//////////////////////////////////////
// Reference for setting up onclicks for a class of button: 
// https://stackoverflow.com/questions/23835150/how-can-i-add-an-event-listener-for-multiple-buttons-with-same-class-name/64032002

///////////////////////////////////////////
// Add an event listener to webpage body //
///////////////////////////////////////////
if (document.body.addEventListener) {
    document.body.addEventListener('click', checkUserClicks, false);
}
// For internet explorer, don't use false option
else {
    document.body.attachEvent('onclick', checkUserClicks);
}

// *************************************************
// * Function to handle any special click features 
// *************************************************
function checkUserClicks(e) {

    // Get html element that user clicked
    e = e || window.event;
    let areaClicked = e.target || e.srcElement;
    // console.log("Area clicked: " + areaClicked.className);

    // ***********************************************************************************************
    // * Check left and right arrow buttins in charge of moving product divs left and right
    // * based on which directional arrow was selected.
    // * Get name of parent container's previous sibling container so we know which area to shift
    // * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Node/parentElement
    // * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Element/previousElementSibling
    // **********************************************************************************************
    if (areaClicked.className.match('left-arrow') || areaClicked.className.match('right-arrow')) {
        // Row container of horizontally-shiftable products
        let productDiv = areaClicked.parentElement.previousElementSibling;
        // * 1) Check each of left buttons
        if (areaClicked.className.match('left-arrow')) 
        {
            // An element of class 'left-btn' was clicked
            productDiv.scrollLeft -= 505;
        }
        // * 2) Check each of right buttons
        if (areaClicked.className.match('right-arrow')) 
        {
            // An element of class 'right-btn' was clicked
            productDiv.scrollLeft += 505;
        }
    }

    // ***********************************************************************************************
    // * Make post request to add a product to a user's personal routine/wishlist when
    // * logged in user selects "add to routine button"
    // ***********************************************************************************************
    // * 3) Check if a product is attempting to be added to routines
    if (areaClicked.className.match('add-to-routine-btn'))
    {
        // Check if user is logged in?

        // An element of class 'add-product-btn' was clicked
        console.log("Add product button clicked!");
        
        // A) Get username
        // B) Get product name




        // fetch('/products', {
        //     method: 'POST',
        //     headers: {
        //         'Accept': 'application/json',
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify({ "id": 78912 })
        // })
        //    .then(response => response.json())
        //    .then(response => console.log(JSON.stringify(response)))
    }

    
}

