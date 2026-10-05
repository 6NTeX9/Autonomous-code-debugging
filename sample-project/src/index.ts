import { createApp } from "./app";

const port = process.env.PORT || 3000;
const app = createApp();

if (process.env.NODE_ENV !== "test") {
  app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
  });
}
