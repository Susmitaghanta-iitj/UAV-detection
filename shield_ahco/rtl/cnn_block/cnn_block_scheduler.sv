module cnn_block_scheduler(
  input logic clk,rst_n,start,
  input logic conv_done,
  input logic pool_done,
  output logic conv_start,
  output logic pool_start,
  output logic mem_swap,
  output logic busy,
  output logic done
);
  typedef enum logic[2:0]{IDLE,CONV,POOL,SWAP,DONE} st_t;
  st_t st;

  always_comb begin
    conv_start=0;pool_start=0;mem_swap=0;done=0;busy=(st!=IDLE && st!=DONE);
    case(st)
      IDLE: if(start) conv_start=1;
      CONV: if(conv_done) pool_start=1;
      SWAP: mem_swap=1;
      DONE: done=1;
      default:;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n) st<=IDLE;
    else begin
      case(st)
        IDLE: if(start) st<=CONV;
        CONV: if(conv_done) st<=POOL;
        POOL: if(pool_done) st<=SWAP;
        SWAP: st<=DONE;
        DONE: st<=IDLE;
        default: st<=IDLE;
      endcase
    end
  end
endmodule
