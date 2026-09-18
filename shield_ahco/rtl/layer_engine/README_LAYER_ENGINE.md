# layer engine layer engine

Software reference now executes Conv1D, Dense, ReLU, and MaxPool1D using the
shared transprecision transprecision MAC model.

RTL now includes feature/weight memories, Conv1D, Dense, ReLU, MaxPool1D, and a
simple operator scheduler.

The source clearly supports sequential layer reuse, FSM scheduling, activation overlap,
feature-memory reuse, and AXI integration. It does not provide enough information to
claim these exact FSMs or handshakes are the author's original RTL.
