.. role:: fwLighter
    :class: fw-lighter

Introduction
============

| Our Snappy New API (short snAPI) is a powerful Python wrapper which enables seamless
| communication and configuration with PicoQuant Time Correlated Single Photon Counting
| Instruments (TCSPC devices). It harnesses the advantages of C++ for optimal speed and
| performance and bridges the gap between the high-speed capabilities of your PicoQuant 
| TCSPC device and the ease of use and versatility of Python.

| snAPI provides a high-level interface to the underlying C++ library and enables users to tap
| into the full potential of your TCSPC device while maintaining the flexibility and versatility
| of the Python programming language. The low-level control offered by C++ ensures smooth
| and efficient data processing, enabling efficient handling of large photon counts and their
| real-time analysis. Additionally, snAPI introduces another dimension of flexibility by
| providing the option to access unfolded data from your PicoQuant TCSPC device. This opens a whole
| new realm of possibilities, allowing researchers, developers, and scientists to delve deeper
| into their data and extract valuable insights.

| By leveraging the power of Python users can build their own algorithms, implement complex
| calculations, and develop tailored data processing pipelines for analysis. With snAPI, users
| can make use of advanced measurement classes such as timetrace, histogram, unfold, raw and
| correlation (e.g, FCS, g2), without worrying about the intricacies of device handling. The
| measurement classes can be sequentially combined with data manipulators (e.g. coincidence,
| herald, merge, delay) to provide maximum flexibility in analysis.

| snAPI is free to use and compatible with PicoQuant `TimeHarp 260 <https://www.picoquant.com/products/time-tagging-tcspc-electronics/timeharp-260/>`_ (drivers optional),
| `MultiHarp 160 <https://www.picoquant.com/products/time-tagging-tcspc-electronics/multiharp-160/>`_, `MultiHarp 150 <https://www.picoquant.com/products/time-tagging-tcspc-electronics/multiharp-150/>`_, `HydraHarp 400 <https://www.picoquant.com/news/hydraharp-400-discontinued/>`_ and `PicoHarp 330 <https://www.picoquant.com/products/time-tagging-tcspc-electronics/picoharp-330/>`_.
| To get started users just need a PicoQuant TCSPC device, its Library/DLL, Python, and snAPI.
