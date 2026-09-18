module dense_complete_engine #(
  parameter DIN=16,
  parameter DOUT=4,
  parameter ACC_W=48,
  parameter CONST_W=32,
  parameter FRAC_W=24
)(
  input logic clk,
  input logic rst_n,
  input logic start,

  input logic signed [CONST_W-1:0] scale_aw_q,
  input logic signed [CONST_W-1:0] scale_al_q,
  input logic signed [CONST_W-1:0] alpha_q,
  input logic signed [CONST_W-1:0] out_scale_q,

  output logic act_req,
  output logic [$clog2(DIN)-1:0] act_addr,
  input logic [7:0] act_data,

  output logic wgt_req,
  output logic [$clog2(DIN*DOUT)-1:0] wgt_addr,
  input logic [7:0] wgt_data,

  output logic bias_req,
  output logic [$clog2(DOUT)-1:0] bias_addr,
  input logic signed [CONST_W-1:0] bias_data,

  output logic out_valid,
  output logic [$clog2(DOUT)-1:0] out_index,
  output logic [7:0] out_code,
  output logic done
);

  typedef enum logic [3:0] {IDLE,CLEAR,LOAD,MAC,FINALIZE,EMIT,NEXT,DONE} state_t;
  state_t st;
  integer i,o;

  logic mac_clear,mac_en;
  logic signed [ACC_W-1:0] sum_qaqw,sum_qa;
  logic signed [79:0] preact_q;
  logic [7:0] final_code;

  qat_affine_mac_core #(.ACT_W(8),.WGT_W(8),.ACC_W(ACC_W)) MAC(
    .clk,.rst_n,.clear(mac_clear),.en(mac_en),
    .act_code(act_data),.wgt_code(wgt_data),
    .sum_qaqw,.sum_qa
  );

  qat_affine_pact_finalize #(
    .ACC_W(ACC_W),.CONST_W(CONST_W),.FRAC_W(FRAC_W),.OUT_W(8)
  ) FIN(
    .sum_qaqw,.sum_qa,
    .scale_aw_q,.scale_al_q,.bias_q(bias_data),
    .alpha_q,.out_scale_q,
    .preact_q,.out_code(final_code)
  );

  always_comb begin
    act_req=0;wgt_req=0;bias_req=0;out_valid=0;done=0;
    mac_clear=0;mac_en=0;

    act_addr=i;
    wgt_addr=o*DIN+i;
    bias_addr=o;
    out_index=o;
    out_code=final_code;

    case(st)
      CLEAR:mac_clear=1;
      LOAD:begin act_req=1;wgt_req=1;end
      MAC:mac_en=1;
      FINALIZE:bias_req=1;
      EMIT:begin bias_req=1;out_valid=1;end
      DONE:done=1;
      default:;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin st<=IDLE;i<=0;o<=0; end
    else begin
      case(st)
        IDLE:if(start)begin i<=0;o<=0;st<=CLEAR;end
        CLEAR:st<=LOAD;
        LOAD:st<=MAC;
        MAC:begin
          if(i==DIN-1)begin i<=0;st<=FINALIZE;end
          else begin i<=i+1;st<=LOAD;end
        end
        FINALIZE:st<=EMIT;
        EMIT:st<=NEXT;
        NEXT:begin
          if(o==DOUT-1)st<=DONE;
          else begin o<=o+1;st<=CLEAR;end
        end
        DONE:st<=IDLE;
        default:st<=IDLE;
      endcase
    end
  end
endmodule
