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

    // **************************************************************************************************
    // * Check left and right arrow buttins in charge of moving product divs left and right
    // * based on which directional arrow was selected.
    // * Get grand-parent DOM and scan through its children until we find the div containing the products
   
    // * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Node/parentElement
    // * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Element/previousElementSibling
    // * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Node/childNodes
    // * Reference: https://www.javascripttutorial.net/javascript-dom/javascript-get-child-element/
    // **************************************************************************************************
    if (areaClicked.className.match('left-arrow') || areaClicked.className.match('right-arrow')) {
        
        // Row container of horizontally-shiftable products
        let productDiv = searchSiblingNodes(areaClicked.parentElement, 'stepContainers');
        
        // * 1) Check each of left buttons
        if (areaClicked.className.match('left-arrow')) {
            // An element of class 'left-btn' was clicked
            productDiv.scrollLeft -= 505;
        }
        // * 2) Check each of right buttons
        if (areaClicked.className.match('right-arrow')) {
            // An element of class 'right-btn' was clicked
            productDiv.scrollLeft += 505;
        }
    }

    // ***********************************************************************************************
    // * Make post request to add a product to a user's personal routine/wishlist when
    // * logged in user selects "add to routine button"
    // ***********************************************************************************************
    // * 3) Check if a product is attempting to be added to routines
    if (areaClicked.className == ('add-to-routine-btn'))
    {
        // An element of class 'add-product-btn' was clicked
        // Get username and product name
        let username = document.getElementById("username").innerText;
        let product = searchSiblingNodes(areaClicked, 'product-name');
        console.log(username)
        let productName = product.innerText;

        // Use JS Fetch to make post request
        // Reference: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
        const data = { username: username, productName: productName };

        // Make POST request to add the selected product to user's routine table
        fetch("/add_to_routine", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        })
          .then((response) => response.json())
          .then((responseData) => {
            console.log("Success:", responseData);
          })
          .catch((error) => {
            console.error("Error:", error);
          });
    }


    // ***********************************************************************************************
    // * Make post request to remove a product from a user's personal routine/wishlist when
    // * logged in user clicks 'remove from routine' button in routine page
    // ***********************************************************************************************
    // * 4) Check if a product is attempting to be removed from a user's routine
    if (areaClicked.className == ('remove-from-routine-btn'))
    {
        // An element of class 'remove-from-routine-btn' was clicked
        // Get username and product name
        let username = document.getElementById("username").innerText;
        let product = searchSiblingNodes(areaClicked, 'product-name');
        let productName = product.innerText;

        // Use JS Fetch to make post request
        // Reference: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
        const data = { username: username, productName: productName };

        // Make post request to delete selected product from user's routine table
        fetch("/remove_from_routine", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        })
          .then((response) => response.json())
          .then((responseData) => {
            console.log("Success:", responseData);
          })
          .catch((error) => {
            console.error("Error:", error);
          });

        // Remove product card from HTML as well
        // Reference: https://stackoverflow.com/questions/12287422/removing-element-dynamically
        let productHTMLNode = areaClicked.parentElement;
        productHTMLNode.parentElement.removeChild(productHTMLNode);
    }

}


// Function that returns a specified sibling node based on a provided start node and a given name
// **********************************************************************************************
// * Start by getting parent's child nodes and look through them until we find the
// * div with the specified classname
// *
// * Reference: https://developer.mozilla.org/en-US/docs/Web/API/Node/childNodes
// * Reference: https://www.javascripttutorial.net/javascript-dom/javascript-get-child-element/
// *********************************************************************************************
function searchSiblingNodes(node, classTargetName) {
    let parent = node.parentElement;
    let siblings = parent.childNodes;
    let targetSibling = null;
    for (var i = 0; i < siblings.length; i++) {
        // Look for product name in div with the class: 'product-name' 
        if (siblings[i].className == classTargetName) {
            targetSibling = siblings[i];
            return targetSibling;
        }
    }
    return targetSibling;
}