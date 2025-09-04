import { SnackbarProvider } from "notistack";
import AppRoutes from "./routes";

const App = () => {
  return (
    <SnackbarProvider maxSnack={3} autoHideDuration={3000}>
      <AppRoutes />
    </SnackbarProvider>
  );
};

export default App;
