import _ from 'underscore';

const DEFAULT_STATE = {
  isAuthenticated: false,
  isAuthenticating: false,
  username: null
};

const authReducer = function (_state, action) {
  let state = _.clone(_state);
  if (typeof state === 'undefined') {
    return DEFAULT_STATE;
  };
  if (action.type === 'AUTHENTICATE_USER') {
    state.isAuthenticated = true;
    state.isAuthenticating = false;
    state.username = 'ipsum123';
    return state;
  } else if (action.type === 'LOGOUT') {
    state.isAuthenticated = false;
    state.isAuthenticating = false;
    state.username = null;
  }
  return state;
};

module.exports = authReducer;
