module ahco_top_shell(
 input logic clk,rst_n,start,
 input logic layer_done,
 output logic layer_start,
 output logic [2:0] layer_id,
 output logic is_conv,is_dense,
 output logic [15:0] cin_din,cout_dout,length,
 output logic [7:0] kernel,pool,
 output logic finished
);
 ahco_global_scheduler S(.clk,.rst_n,.start,.layer_done,.layer_start,.layer_id,.finished);
 ahco_layer_config_rom C(.layer_id,.is_conv,.is_dense,.cin_din,.cout_dout,.length,.kernel,.pool);
endmodule
