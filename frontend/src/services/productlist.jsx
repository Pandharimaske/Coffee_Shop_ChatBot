import { fireBaseDB } from "../config/firebaseConfig";
import { ref, get } from "firebase/database";

const productsRef = ref(fireBaseDB, "products");

const fetchProducts = async () => {
  const snapshot = await get(productsRef);
  const data = snapshot.val();

  const products = [];
  if (data) {
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        products.push({ ...data[key] });
      }
    }
  }

  return products;
};

export { fetchProducts };
