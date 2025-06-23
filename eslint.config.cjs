module.exports = [
  // 1) Ignore dependencies
  {
    ignores: ["node_modules/"],
  },
  // 2) Lint your source files
  {
    files: ["src/**/*.js"],
    extends: ["eslint:recommended"],
    languageOptions: {
      parserOptions: {
        ecmaVersion: 2021,
        sourceType: "module",
      },
      globals: {
        require: "readonly",
        module: "readonly",
        console: "readonly",
        process: "readonly",
      },
    },
    rules: {
      // add any custom rules
    },
  },
];
