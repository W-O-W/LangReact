from dataclasses import MISSING, dataclass, field

@dataclass(kw_only=True)
class InvokeParams:
    application:str = field(default=MISSING)

    search_application:str = field(default=None)
    cot:bool = field(default=False)
    reflection:bool = field(default=False)
    # refine:bool = field(default=True)
    web_retrieve:bool = field(default=False)
    memory_retrieve:bool = field(default=True)
    max_step_num:int = field(default=3)

    
    #web retrieve
    web_reference_num:int = field(default=3)
    #reflection configure
    reflection_new_session:bool = field(default=True)


    #memory_retrieve conf
    memory_retrieve_only_user:bool = field(default=True)
    memory_retrieve_num:int = field(default=30)
    memory_max_choice_num:int = field(default=3)
    memory_adjust_choice:bool = field(default=True)
    #memory adjust choice conf
    memory_min_similarity_threshold:float = field(default=0.1)
    memory_rerank:bool = field(default=True)
    memory_rerank_plugin:str = field(default=None)

    #cot conf
    # custom_examples:List[GlobalMemoryChunk] = field(default_factory=list)
    tot_mode:bool = field(default=False)
    plan_role:str = field(default="user")
    #step by step 
    step_by_step:bool = field(default=False)
    step_adjust_planning:bool = field(default=False)
    # cot
    cot_max_step_num:int = field(default=6)
    cot_memory_aid:bool = field(default=True)
    cot_reflection:bool = field(default=False)
    cot_new_session:bool = field(default=True)
    cot_web_retrieve:bool = field(default=False)
    cot_conclude:bool = field(default=True)
    # tot
    tot_max_depth:int = field(default=3)

