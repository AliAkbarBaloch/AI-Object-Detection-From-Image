import { useSnackbar } from "notistack";

const Notification = () => {
  const { enqueueSnackbar } = useSnackbar();
  return { enqueueSnackbar };
};

export default Notification;
