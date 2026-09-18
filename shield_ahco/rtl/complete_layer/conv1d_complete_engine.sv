module conv1d_complete_engine #(
  parameter CIN=2,
  parameter COUT=3,
  parameter LENGTH=8,
  parameter K=3,
  parameter STRIDE=1,
  parameter PADDING=1,
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

  output logic in_req,
  output logic [$clog2(CIN*LENGTH)-1:0] in_addr,
  input logic [7:0] in_data,

  output logic wgt_req,
  output logic [$clog2(COUT*CIN*K)-1:0] wgt_addr,
  input logic [7:0] wgt_data,

  output logic bias_req,
  output logic [$clog2(COUT)-1:0] bias_addr,
  input logic signed [CONST_W-1:0] bias_data,

  output logic out_valid,
  output logic [$clog2(COUT)-1:0] out_oc,
  output logic [$clog2(((LENGTH+2*PADDING-K)/STRIDE)+1)-1:0] out_ox,
  output logic [7:0] out_code,
  output logic done
);

  localparam OUTL=((LENGTH+2*PADDING-K)/STRIDE)+1;

  typedef enum logic [3:0] {IDLE,CLEAR,LOAD,MAC,FINALIZE,EMIT,ADV,DONE} state_t;
  state_t st;
  integer oc,ox,ic,kk,ix;

  logic [7:0] act_mux;
  logic mac_clear,mac_en;
  logic signed [ACC_W-1:0] sum_qaqw,sum_qa;
  logic signed [79:0] preact_q;
  logic [7:0] final_code;

  always_comb begin
    ix=ox*STRIDE+kk-PADDING;
    act_mux=(ix<0 || ix>=LENGTH) ? 8'h00 : in_data;
  end

  qat_affine_mac_core #(.ACT_W(8),.WGT_W(8),.ACC_W(ACC_W)) MAC(
    .clk,.rst_n,.clear(mac_clear),.en(mac_en),
    .act_code(act_mux),.wgt_code(wgt_data),
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
    in_req=0;wgt_req=0;bias_req=0;out_valid=0;done=0;
    mac_clear=0;mac_en=0;
    if(ix<0 || ix>=LENGTH) in_addr='0;
    else in_addr=ic*LENGTH+ix;
    wgt_addr=(oc*CIN+ic)*K+kk;
    bias_addr=oc;
    out_oc=oc;
    out_ox=ox;
    out_code=final_code;

    case(st)
      CLEAR:mac_clear=1;
      LOAD:begin if(ix>=0 && ix<LENGTH)in_req=1;wgt_req=1;end
      MAC:mac_en=1;
      FINALIZE:bias_req=1;
      EMIT:begin bias_req=1;out_valid=1;end
      DONE:done=1;
      default:;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n)begin st<=IDLE;oc<=0;ox<=0;ic<=0;kk<=0;end
    else begin
      case(st)
        IDLE:if(start)begin oc<=0;ox<=0;ic<=0;kk<=0;st<=CLEAR;end
        CLEAR:st<=LOAD;
        LOAD:st<=MAC;
        MAC:begin
          if(kk==K-1)begin
            kk<=0;
            if(ic==CIN-1)begin ic<=0;st<=FINALIZE;end
            else begin ic<=ic+1;st<=LOAD;end
          end else begin kk<=kk+1;st<=LOAD;end
        end
        FINALIZE:st<=EMIT;
        EMIT:st<=ADV;
        ADV:begin
          if(ox==OUTL-1)begin
            ox<=0;
            if(oc==COUT-1)st<=DONE;
            else begin oc<=oc+1;st<=CLEAR;end
          end else begin ox<=ox+1;st<=CLEAR;end
        end
        DONE:st<=IDLE;
        default:st<=IDLE;
      endcase
    end
  end
endmodule
