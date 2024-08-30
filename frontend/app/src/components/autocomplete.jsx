import { useState } from "react";
import clsx from "clsx";
import { ListItem, UiFieldInput } from "./";


export function Autocomplete({completions=null, getMatchesCallback=null, showMatchesCallback=null, suggestionResolver=null, className, inputProps}) {    
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const emptySuggestion = "No matches found.";

    if (!completions && !getMatchesCallback) {
        throw "Either completions or getCompletionsCallback must be provided";
    }

    const handleSuggestionClick = (value) => {
        setInputValue(value);
        setSuggestions([]);
    };

    const handleInputChange = (event) => {
        const value = event.target.value;
        setInputValue(value);
        if (value.length > 0) {
          var filteredSuggestions
          if (completions) {
            filteredSuggestions = completions.filter(suggestion =>
                suggestion.toLowerCase().includes(value.toLowerCase())
            );
            setSuggestions(filteredSuggestions.length > 0 ? filteredSuggestions : [emptySuggestion]);
          } else if (getMatchesCallback) {
            const returnedPromise = getMatchesCallback(value);
            if (!(returnedPromise instanceof Promise)) throw "getMatchesCallback must return a promise but got " + typeof returnedPromise;
            returnedPromise.then((matches) => {
                setSuggestions(matches.length > 0 ? matches : [emptySuggestion]);
            }).catch((error) => setSuggestions([emptySuggestion]));
          }
          console.log(suggestions);
        } else {
          setSuggestions([]);
        }
    };

    const resolveSuggestion = (suggestion) => {
        if (typeof suggestion === 'object') {
            if (!suggestionResolver) throw "If suggestion type is object suggestionResolver must be provided to resolve value.";
            return suggestionResolver(suggestion);
        }
        return suggestion;
    }

    return (
        <div className={clsx(className)}>
            <UiFieldInput {...inputProps} onChange={handleInputChange} value={inputValue} {...inputProps}></UiFieldInput>
            {suggestions.length > 0 && (
                <ul className="bg-white">
                    {suggestions.map((suggestion, index) => {
                        let suggestionValue = resolveSuggestion(suggestion)
                        return (
                            <ListItem key={index} onClick={() => handleSuggestionClick(suggestionValue)}>
                                {showMatchesCallback ? showMatchesCallback(suggestion, inputValue) : suggestionValue}
                            </ListItem>
                        );
                    })}
                </ul>
            )}
        </div>
    )
}