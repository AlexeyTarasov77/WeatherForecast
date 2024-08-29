class Autocomplete {
    constructor(completions=[], getCompletionsCallback=null) {
        if (!completions && !getCompletionsCallback) {
            throw "Either completions or getCompletionsCallback must be provided";
        }
        this._completions = completions;
        this._dataCallback = getCompletionsCallback;
        this._currentFocus = null;
    }

    onInput() {

    }
    addActive(items) {
      /*a function to classify an item as "active":*/
      if (!items) return false;
      /*start by removing the "active" class on all items:*/
      this.removeActive(items);
      if (this._currentFocus >= items.length) this._currentFocus = 0;
      if (this._currentFocus < 0) this._currentFocus = (items.length - 1);
      /*add class "autocomplete-active":*/
      items[currentFocus].classList.add("autocomplete-active");
    }
    removeActive(items) {
      /*a function to remove the "active" class from all autocomplete items:*/
      for (var i = 0; i < items.length; i++) {
        items[i].classList.remove("autocomplete-active");
      }
    }
    closeAllLists(el) {
      /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
      var autocompleteItems = document.getElementsByClassName("autocomplete-items");
      for (var i = 0; i < autocompleteItems.length; i++) {
        if (el != autocompleteItems[i] && el != inp) {
        autocompleteItems[i].parentNode.removeChild(autocompleteItems[i]);
      }
    }
  }
}


export function autocomplete(inp, completions=[], getCompletionsCallback=null) {
    if (!completions && !getCompletionsCallback) {
        throw "Either completions or getCompletionsCallback must be provided";
    }
    const citiesURL = "https://api.thecompaniesapi.com/v1/locations/cities"
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function() {
        let val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val || val.length < 3) { return false;}
        var cities = []
        fetch(citiesURL, {
            method: "GET",
            body: {
                token: 'fUrFHu1E',
                search: val
            }
        })
        .then((resp) => resp.json())
        .then((data) => {
            data.forEach(city => {
                cities.push({cityName: city.name, countryName: city.country.name})
            });
        })
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        let autocompleteList = document.createElement("DIV");
        autocompleteList.setAttribute("id", this.id + "autocomplete-list");
        autocompleteList.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(autocompleteList);
        /*for each item in the array...*/
        for (let i = 0; i < cities.length; i++) {
          /*check if the item starts with the same letters as the text field value:*/
          const citySubstr = cities[i].cityName.substr(0, val.length)
          if (citySubstr.toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            const autocompleteItemHtml = `
                <div>
                    <strong>${citySubstr}</strong> ${cities[i].substr(val.length)}
                    <p>${cities[i].countryName}</p>
                    <input type='hidden' value='${cities[i].cityName}'>
                </div>
            `
            const autocompleteItem = document.createElement('div')
            autocompleteItem.innerHTML = autocompleteItemHtml
            /*execute a function when someone clicks on the item value (DIV element):*/
            autocompleteItem.addEventListener("click", function() {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            autocompleteList.appendChild(autocompleteItem);
          }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var autocompletes = document.getElementById(this.id + "autocomplete-list");
        if (autocompletes) autocompletes = autocompletes.getElementsByTagName("div");
        if (e.keyCode == 40) {
          /*If the arrow DOWN key is pressed,
          increase the currentFocus variable:*/
          currentFocus++;
          /*and and make the current item more visible:*/
          addActive(autocompletes);
        } else if (e.keyCode == 38) { //up
          /*If the arrow UP key is pressed,
          decrease the currentFocus variable:*/
          currentFocus--;
          /*and and make the current item more visible:*/
          addActive(autocompletes);
        } else if (e.keyCode == 13) {
          /*If the ENTER key is pressed, prevent the form from being submitted,*/
          e.preventDefault();
          if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (autocompletes) autocompletes[currentFocus].click();
          }
        }
    });
    function addActive(items) {
      /*a function to classify an item as "active":*/
      if (!items) return false;
      /*start by removing the "active" class on all items:*/
      removeActive(items);
      if (currentFocus >= items.length) currentFocus = 0;
      if (currentFocus < 0) currentFocus = (items.length - 1);
      /*add class "autocomplete-active":*/
      items[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(items) {
      /*a function to remove the "active" class from all autocomplete items:*/
      for (var i = 0; i < items.length; i++) {
        items[i].classList.remove("autocomplete-active");
      }
    }
    function closeAllLists(el) {
      /*close all autocomplete lists in the document,
      except the one passed as an argument:*/
      var autocompleteItems = document.getElementsByClassName("autocomplete-items");
      for (var i = 0; i < autocompleteItems.length; i++) {
        if (el != autocompleteItems[i] && el != inp) {
        autocompleteItems[i].parentNode.removeChild(autocompleteItems[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}
