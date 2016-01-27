import React from 'react';
import ReactDOM from 'react-dom';
import 'babel/polyfill'; // allow promise

const ReduxApplication = require('./redux_application.jsx');
// *** STARTS THE BROWSER APPLICATION ***
// ------------------*-------------------
console.log('hello')
ReactDOM.render(<ReduxApplication />, document.getElementById('j-application'));
