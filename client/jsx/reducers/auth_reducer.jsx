const DEFAULT_STATE = {
  isAuthenticated: false
};

const authReducer = function (state, action) {
  if (typeof state === 'undefined') {
    return DEFAULT_STATE;
  };
  return state;
};

module.exports = authReducer;
