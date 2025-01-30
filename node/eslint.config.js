// eslint.config.js
export default [
    {
      ignores: ["node_modules"],
    },
    {
      files: ["src/**/*.js"], // もしくは ts など
      languageOptions: {
        ecmaVersion: "latest",
        sourceType: "module"
      },
      rules: {
        // ここでルール指定。例:
        "semi": ["error", "always"],
        "quotes": ["error", "single"]
      }
    }
  ];