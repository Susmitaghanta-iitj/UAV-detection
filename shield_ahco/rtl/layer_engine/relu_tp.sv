module relu_tp(input logic [1:0] mode,input logic [7:0] in_code,output logic [7:0] out_code);
 logic is_nar; logic signed [31:0] v; logic signed [47:0] rv;
 tp_decode D(.mode(mode),.code(in_code),.is_nar(is_nar),.value_q16_16(v));
 always_comb begin
   if(is_nar) rv={{16{v[31]}},v};
   else if(v<0) rv='0;
   else rv={{16{v[31]}},v};
 end
 tp_output_encode E(.mode(mode),.nar_seen(is_nar),.x_q16_16(rv),.out_code(out_code));
endmodule
