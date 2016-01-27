import React from 'react';
import { Route } from 'react-router';

// import handler containers
const Layout = require('./containers/layout.jsx');

const Index = require('./containers/index.jsx');
const ExampleContainer = require('./containers/example_container.jsx');
const Login = require('./containers/login.jsx');
const NotFound = require('./containers/not_found.jsx');

module.exports = (
  <Route path='/' component={Layout}>
    <Route path='dashboard' component={Index} />
    <Route path='login' component={Login} />
    <Route path='*' component={NotFound}/>
  </Route>
);
