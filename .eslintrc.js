module.exports = { 
  "overrides": [
    {
      "files": ["oarepo_requests/ui/theme/assets/semantic-ui/js/oarepo_requests_ui/**/*"],
      "env": {
        "browser": true,
        "es2021": true
      },
      "extends": [ 
        "eslint:recommended", 
        "plugin:react/recommended", 
        "plugin:react-hooks/recommended",
        "plugin:jsx-a11y/recommended" 
      ], 
      "parserOptions": {
        "sourceType": "module",
        "ecmaFeatures": {
          "jsx": true
        }
      },
      "settings": {
        "react": {
          "version": "detect"
        }
      },
      "plugins": ["react", "react-hooks", "jsx-a11y"],
      "rules": {
        "react/prop-types": "off",
      }
    }
  ]
}