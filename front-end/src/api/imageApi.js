
import api from "./axiosConfig";

// Batch upload for multiple images
export const uploadImagesBatch = async (files, itemType) => {
  const user_id = localStorage.getItem("user_id");
  if (!user_id) {
    throw new Error("User is not logged in");
  }
  const formData = new FormData();
  for (let file of files) {
    formData.append("images", file);
  }
  formData.append("item_type", itemType);
  formData.append("user_id", user_id);
  const { data } = await api.post("Counting/batch_count", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    method: "POST",
    body: formData,
  });
  return data;
};

export const uploadImage = async (file, itemType) => {
  const user_id = localStorage.getItem("user_id");

  if (!user_id) {
    throw new Error("User is not logged in");
  }
  const formData = new FormData();
  formData.append("image", file);
  formData.append("item_type", itemType);
  formData.append("user_id", user_id); // ✅ Append user_id to formData
  console.log("Uploading image with user_id:", user_id);  

  const { data } = await api.post("Counting/count", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    method: "POST",
    body: formData,
  });

  return data;
};

export const correctResult = async ({ result_id, correct_count }) => {
  const { data } = await api.post("/Correction/correct", {
    result_id,
    correct_count,
  });
  return data;
};


export const loginUser = async (email, password) => {
  const { data } = await api.post(
    "/Auth/login",
    {
      email,
      password,
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  // ✅ Save user_id in localStorage after login
  if (data?.user_id) {
    console.log(data.user_id);
    
    localStorage.setItem("user_id", data.user_id);
  }

  return data;
};

export const registerUser = async (name, email, password) => {
  const { data } = await api.post("/Auth/register", {
    name,
    email,
    password,
  });
  return data;
};

export const getPreviousResults = async () => {
  // ✅ Get stored user_id from localStorage
  const user_id = localStorage.getItem("user_id");

  if (!user_id) {
    throw new Error("User is not logged in");
  }

  // ✅ Send user_id as query parameter
  const { data } = await api.get(`/Auth/previous-results?user_id=${user_id}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  return data;
};
