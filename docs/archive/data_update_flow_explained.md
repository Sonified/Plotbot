# Plotbot's Kitchen: How Your Data Gets Cooked!

Imagine Plotbot is a super-smart Chef, and you've just asked it to cook up a delicious data plot. Let's say you want a plot showing the Sun's magnetic field and some zippy solar wind particles for a specific week.

Here's how Chef Plotbot gets your meal ready:

**1. The Order Comes In: `plotbot(trange, *variables)`**

*   You: "Chef Plotbot, I'd like a plot for 'this week' (`trange`) showing 'magnetic field data' and 'proton data' (`*variables`)."
*   This is like placing your order at the restaurant. The `plotbot` function is the main waiter taking your request.

**2. Checking the Pantry & Shopping List: `get_data()` and `global_tracker`**

*   Before rushing to the market, Chef Plotbot has a helper, `get_data`, who first checks the pantry.
*   `get_data` asks the **`global_tracker`** (think of this as the kitchen's meticulous inventory manager): "Do we already have fresh 'magnetic field data' and 'proton data' for 'this week'?"
*   The `global_tracker` keeps a detailed list of all ingredients (data types like `'mag_RTN_4sa'` or `'spi_sf00_l3_mom'`) and for which dates they've been stocked.
    *   If the `global_tracker` says, "Yep, all stocked and fresh for that week!", `get_data` is happy.
    *   If not, it's time to go shopping!

**3. Going to the Market (If Needed): Downloading and `import_data_function`**

*   If the `global_tracker` says, "Nope, we're out of 'proton data' for Tuesday of 'this week'," then `get_data` initiates a shopping trip.
*   **Downloading:** If the raw ingredients (CDF or CSV files) aren't even in the local storeroom, Plotbot might first download them from the internet (like going to a specific farmers' market – SPDF or Berkeley servers).
*   **`import_data_function` (The Prep Cook):** Once the raw files are available locally, `import_data_function` is like a specialized prep cook.
    *   It takes the raw files for the specific `trange` and `data_type` (e.g., "proton data files for this Tuesday").
    *   It reads them, cleans them up a bit, and puts all the relevant numbers and times into a neat temporary container called a `DataObject`. Think of this as chopping vegetables and putting them in a prep bowl.

**4. Stocking the Main Kitchen Stations: The `DataCubby` and Global Instances!**

*   This is where the **`DataCubby`** shines! Imagine the `DataCubby` as the head chef's personal, organized set of ingredient stations or "cubbies" in the main kitchen.
*   There's a cubby for `mag_rtn_4sa` (magnetic field), another for `proton` (solar wind particles), and so on for each major data type. These are the "global instances" – the main, ready-to-use batches of ingredients.
*   The `DataObject` (our prep bowl of chopped veggies) from `import_data_function` is handed over to the `DataCubby`.
*   The `DataCubby` then says to the specific global instance (e.g., the main `plotbot.mag_rtn_4sa` object): "Hey, I've got new stuff for you!" and calls its `.update()` method.

**5. Refreshing the Ingredient Stations: The Data Class `.update()` Method**

*   The `.update()` method of a data class (like `mag_rtn_4sa_class.update()`) is like the chef at that specific station taking the new prepped ingredients from the `DataObject` and refreshing their main supply.
*   They'll:
    *   Update their main list of timestamps (`datetime_array`).
    *   Update their containers of actual data (`raw_data['br']`, `raw_data['density']`, etc.).
    *   Crucially, they also refresh any associated `plot_manager` instances. Think of `plot_manager`s as little display cards that know how to present that specific ingredient (e.g., "plot Br field in green"). These need to be updated to point to the new, fresh data.

**6. Updating the Inventory List: `global_tracker` Again**

*   Once the `DataCubby` has successfully helped update the main ingredient station (the global instance), `get_data` tells the `global_tracker`: "Okay, 'proton data' for 'this week' is now fully stocked and fresh!" The inventory list is updated.

**What About Special Recipes? (Calculated Properties like `br_norm`)**

*   Some "dishes" Plotbot makes, like `mag_rtn_4sa.br_norm` (magnetic field strength normalized by distance), aren't raw ingredients you fetch directly. They are *calculated* from other ingredients.
*   **Chef's Special Calculation:** `br_norm` needs `Br` (a component of magnetic field data from `mag_rtn_4sa`) and `R` (distance from the Sun, which might come from the `proton` data).
*   **Lazy Cooking & Smart Caching:** Plotbot is smart. It usually only calculates `br_norm` when you actually ask for it (lazy calculation). Once calculated, it might keep the result handy (caching) if you ask for it again quickly.
*   **Keeping it Fresh:**
    *   When the main `mag_rtn_4sa` ingredient station gets new data (because its `.update()` method was called), it knows that any previously calculated `br_norm` might be stale.
    *   So, in its `.update()` method, `mag_rtn_4sa` will basically throw away the old `br_norm` calculation (e.g., by setting `self._br_norm_manager = None`).
    *   The next time you ask for `br_norm`, the `@property` method for `br_norm` sees the cached version is gone. It then automatically re-runs its calculation (`_calculate_br_norm()`), using the *newly updated* `Br` and `R` values. This ensures your calculated dish is always made with the freshest base ingredients for the current time range!

**In a Nutshell:**

1.  **Order Up!** (`plotbot` function)
2.  **Check Pantry & List** (`get_data` asks `global_tracker`)
3.  **Go Shopping & Prep** (Downloads & `import_data_function` creates a `DataObject`)
4.  **Stock Head Chef's Stations** (`DataCubby` tells global instances like `plotbot.mag_rtn_4sa` to update themselves using the `DataObject`)
5.  **Refresh Ingredient Stations** (Global instances call their own `.update()` methods)
6.  **Update Inventory** (`global_tracker` notes fresh stock)
7.  **Special Recipes** (Calculated properties like `br_norm` get invalidated by their parent's `.update()` and recalculate on demand)

The `DataCubby` is like the quartermaster of the kitchen, ensuring that the main, named ingredient stations (the global instances like `plotbot.mag_rtn_4sa` or `plotbot.proton`) are the ones that get updated with the freshly prepped ingredients (`DataObject` from `import_data_function`). It's the bridge between temporary prepped data and the persistent, ready-to-use data sources in Plotbot's kitchen. 