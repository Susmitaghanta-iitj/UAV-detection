module block_latency1_scheduler(
  input logic clk,rst_n,start,
  input logic conv_done,
  input logic pool_done,
  output logic conv_start,
  output logic pool_start,
  output logic mem_swap,
  output logic busy,
  output logic done
);
  typedef enum logic[2:0] {IDLE,START_CONV,RUN_CONV,START_POOL,RUN_POOL,SWAP,DONE} st_t;
  st_t st;

  always_comb begin
    conv_start=0;pool_start=0;mem_swap=0;done=0;
    busy=(st!=IDLE && st!=DONE);

    case(st)
      START_CONV: conv_start=1;
      START_POOL: pool_start=1;
      SWAP: mem_swap=1;
      DONE: done=1;
      default:;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n) st<=IDLE;
    else begin
      case(st)
        IDLE: if(start) st<=START_CONV;
        START_CONV: st<=RUN_CONV;
        RUN_CONV: if(conv_done) st<=START_POOL;
        START_POOL: st<=RUN_POOL;
        RUN_POOL: if(pool_done) st<=SWAP;
        SWAP: st<=DONE;
        DONE: st<=IDLE;
        default: st<=IDLE;
      endcase
    end
  end
endmodule
